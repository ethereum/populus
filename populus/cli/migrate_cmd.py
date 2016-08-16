import click

import gevent

from populus.utils.filesystem import (
    ensure_path_exists,
)
from populus.utils.transactions import (
    is_account_locked,
    wait_for_unlock,
)
from populus.utils.cli import (
    select_chain,
    select_account,
    request_account_unlock,
    deploy_contract_and_verify,
    show_chain_sync_progress,
)
from populus.migrations.migration import (
    get_migration_classes_for_execution,
)
from populus.migrations.validation import (
    validate_migration_classes,
)

from .main import main


@main.group(
    'migrate',
    invoke_without_command=True,
)
@click.option(
    'chain_name',
    '--chain',
    '-c',
    help=(
        "Specifies the chain that should be migrated. The chains "
        "mainnet' and 'morden' are pre-configured to connect to the public "
        "networks.  Other values should be predefined in your populus.ini"
    ),
)
@click.pass_context
def migrate(ctx, chain_name):
    """
    Run project migrations
    """
    if ctx.invoked_subcommand is not None:
        return
    project = ctx.obj['PROJECT']

    if not project.migrations:
        raise click.Abort((
            "The project does not appear to have any migrations.  You can use "
            "the `populus makemigration command to generate project migrations"
        ))

    # Validate the project migrations
    validate_migration_classes(project.migrations)

    # Determine which chain should be used.
    if not chain_name:
        chain_name = select_chain(project)

    chain_config = project.config.chains[chain_name]

    # Determine if the chain is *migratable*
    if 'registrar' not in chain_config:
        # TODO: this should be a property of the chain object itself.
        # Something like `chain.is_ready_for_migrations`.
        if chain_name not in {'testrpc', 'temp'}:
            # ignore `testrpc` and `temp` because they lazily create their
            # registrar contracts.
            # TODO: We can present the use with the option to just initialize
            # the chain right here rather than throwing an error.
            raise click.Abort((
                "The chain {0!r} is not ready for migrations.  Please initialize this "
                "chain with the `populus migrate init` command".format(chain_name)
            ))

    with project.get_chain(chain_name) as chain:
        web3 = chain.web3

        if chain_name in {'mainnet', 'morden'}:
            show_chain_sync_progress(chain)

        # TODO: pull in the block of code that selects an account
        account = web3.eth.coinbase

        # Unlock the account if needed.
        if is_account_locked(web3, account):
            try:
                wait_for_unlock(web3, account, 2)
            except gevent.Timeout:
                request_account_unlock(chain, account, None)

        # Wait for chain sync if this is a public network.
        if chain_name in {'mainnet', 'morden'}:
            show_chain_sync_progress(chain)

        # Determine if we have any migrations to run.
        migrations_to_execute = get_migration_classes_for_execution(
            project.migrations,
            chain,
        )

        if not migrations_to_execute:
            raise click.Abort(("All migrations have been run."))

        click.echo("Migration operations to perform:")

        for migration in migrations_to_execute:
            click.echo(''.join((
                "  ",
                migration.migration_id,
                " ({0} operations)".format(len(migration.operations)),
                ":",
            )))
            for operation_index, operation in enumerate(migration.operations):
                click.echo(''.join((
                    "    ",
                    str(operation_index),
                    " - ",
                    str(operation),
                )))

        click.echo("Executing migrations:")
        for migration in migrations_to_execute:
            click.echo(''.join((
                "  ",
                migration.migration_id,
                "... ",
            )), nl=False)
            migration.execute()
            click.echo(" DONE")


@migrate.command('init')
@click.option(
    'chain_name',
    '--chain',
    '-c',
    help=(
        "Specifies the chain that should be initialized. The chains "
        "mainnet' and 'morden' are pre-configured to connect to the public "
        "networks.  Other values should be predefined in your populus.ini"
    ),
)
@click.pass_context
def migrate_init(ctx, chain_name):
    """
    Prepare the current chain for migrations.

    contract onto this chain as well as
    """
    project = ctx.obj['PROJECT']

    ensure_path_exists(project.migrations_dir)

    # Determine which chain should be used.
    if not chain_name:
        chain_name = select_chain(project)

    chain_section_name = "chain:{0}".format(chain_name)

    chain_config = project.config.chains[chain_name]

    if chain_name == 'testrpc':
        ctx.abort("Cannot initialize the {0!r} chain".format(chain_name))

    # The `mainnet` and `morden` chains have default configurations.  If the
    # user is working on one of these chains then we need to add the section
    # header so that we can write new config to it.
    if not project.config.has_section(chain_section_name):
        project.config.add_section(chain_section_name)

    chain = project.get_chain(chain_name)

    if 'registrar' not in chain.chain_config:
        # We need to deploy the registrar
        with chain:
            web3 = chain.web3

            if chain_name in {'mainnet', 'morden'}:
                show_chain_sync_progress(chain)

            # Choose the address we should deploy from.
            if 'deploy_from' in chain_config:
                account = chain_config['deploy_from']
                if account not in web3.eth.accounts:
                    raise click.Abort(
                        "The chain {0!r} is configured to deploy from account {1!r} "
                        "which was not found in the account list for this chain. "
                        "Please ensure that this account exists.".format(
                            chain_name,
                            account,
                        )
                    )
            else:
                account = select_account(chain)
                set_as_deploy_from_msg = (
                    "Would you like set the address '{0}' as the default"
                    "`deploy_from` address for the '{1}' chain?".format(
                        account,
                        chain_name,
                    )
                )
                if click.confirm(set_as_deploy_from_msg):
                    project.config.set(chain_section_name, 'deploy_from', account)
                    click.echo(
                        "Wrote updated chain configuration to '{0}'".format(
                            project.write_config()
                        )
                    )

            # Unlock the account if needed.
            if is_account_locked(web3, account):
                try:
                    wait_for_unlock(web3, account, 2)
                except gevent.Timeout:
                    request_account_unlock(chain, account, None)

            # Configure web3 to now send from our chosen account by default
            web3.eth.defaultAccount = account

            # Deploy the registrar
            RegistrarFactory = chain.RegistrarFactory
            registrar = deploy_contract_and_verify(RegistrarFactory, 'Registrar')

            # TODO: set the value in the registrar.

            # Write the registrar address to the chain config
            project.config.set(chain_section_name, 'registrar', registrar.address)
            config_file_path = project.write_config()

            click.echo("Wrote updated chain configuration to {0!r}".format(
                config_file_path,
            ))

    click.echo("The '{0}' blockchain is ready for migrations.".format(
        chain_name
    ))
