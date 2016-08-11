import itertools
import click

from .main import main


@main.group(
    'migrate',
    invoke_without_command=True,
)
@click.pass_context
def migrate(ctx):
    """
    Run project migrations
    """
    if ctx.invoked_subcommand is None:
        click.echo("Invoked migration command")
        # run the migrations
        pass


@migrate.command('init')
@click.pass_context
def migrate_init(ctx):
    """
    Prepare the current chain for migrations.

    contract onto this chain as well as
    """
    project = ctx.obj['PROJECT']

    # First determine which chain should be used.
    if project.chain:
        chain = project.chain
    else:
        chain_options = set(project.config.chains.keys())
        while True:
            choose_chain_msg = "\n".join(itertools.chain((
                "Available Chains",
            ), (
                "- {0}".format(chain_name)
                for chain_name in sorted(chain_options)
            ), (
                "",
                "Type the name of chain you would like to initialize"
            )))
            chain = click.prompt(choose_chain_msg)
            if chain in chain_options:
                break
            click.echo(
                "Invalid chain name: {0!r}.  Please choose from one of the "
                "provided options.".format(chain)
            )

    # Now determine if this chain has accounts.
