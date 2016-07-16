import os
import sys
import textwrap

import click

try:
    from IPython.terminal.embed import InteractiveShellEmbed as InteractiveConsole
    is_ipython = True
except ImportError:
    from code import InteractiveConsole
    is_ipython = False

from eth_rpc_client import Client
from watchdog.events import FileSystemEventHandler

import populus
from populus import utils
from populus.contracts import (
    package_contracts,
)
from populus.geth import (
    get_active_data_dir,
    get_latest_known_instances,
    add_to_known_contracts,
)
from populus.deployment import (
    deploy_contracts,
    validate_deployed_contracts,
)
from populus.cli.deploy_cmd import (
    echo_post_deploy_message,
)
from populus.observers import (
    get_active_dir_observer,
)
from .main import main


def deploy_set(context, client, project_dir, data_dir=None, record=True, contracts_by_name=[]):
    """ Re-Deploy a set of contracts by name or all contracts
        @param context local context for the attach python interpreter.
        @param client RPC client for accessing the ethereum chain
        @param project_dir absolute file path of the project that
            will be interrogated to determine the contracts that
            can be deployed
        @param data_dir directory of the test chain if not None
        @param contracts_by_name Optional argument, this must be an
            iterable of strings indicating the names of the contracts
            to deploy. An empty list deploys all the contracts.
    """
    contracts = package_contracts(utils.load_contracts(project_dir))
    deployed_contracts = deploy_contracts(
        deploy_client=client,
        contracts=contracts,
        deploy_at_block=1,
        max_wait_for_deploy=120,
        from_address=None,
        max_wait=120,
        contracts_to_deploy=contracts_by_name,
        dependencies=None,
        constructor_args=None,
        deploy_gas=None,
    )
    validate_deployed_contracts(client, deployed_contracts)
    echo_post_deploy_message(client, deployed_contracts)
    if data_dir is not None and record:
        add_to_known_contracts(deployed_contracts, data_dir)
    # Update the attach shell's context with the latest contracts
    # objects
    context["contracts"] = contracts
    if data_dir is not None:
        setup_known_instances(context, data_dir)
    return(deployed_contracts)


def setup_known_instances(context, data_dir):
    """ Setup the known instances on the contract objects.
    """
    latest_cts = get_latest_known_instances(context["contracts"], data_dir)
    for name, ct in context["contracts"]:
        if name in latest_cts.keys():
            addr_list = latest_cts[name]
            addr_list.sort(key=lambda r: r[0])
            known_cts = [ct(x[1], context["client"]) for x in addr_list]
            setattr(ct, "known", known_cts)
        else:
            setattr(ct, "known", [])


class ActiveDataDirChangedEventHandler(FileSystemEventHandler):
    """ Active Test Chain Data Directory Symlink Changed Event Handler
        This event handler wait for the create event and then updates
        the known contract instances for that test chain.
    """
    def __init__(self, *args, **kwargs):
        """ User must pass in the attach context and project dir
        """
        self.project_dir = kwargs.pop('project_dir')
        self.context = kwargs.pop('context')

    def on_any_event(self, event):
        if hasattr(event, "dest_path"):
            # This indicates that the event was a creation of the
            # active data symlink and not the delete.

            path = event.src_path
            activePath = get_active_data_dir(self.project_dir)
            if os.path.normpath(path) == os.path.normpath(activePath):
                # This means that a new active chain directory symlink
                # was created and we can refresh our known contracts
                newDataPath = os.readlink(activePath)
                message = (
                    "\n=========== Active Directory Changed ===========\n"
                    "New Active Dir: {active_dir}\n"
                ).format(active_dir=newDataPath)
                click.echo(click.style(message, fg="yellow"))

                # Update the known
                setup_known_instances(self.context, activePath)


@main.command()
@click.option(
    '--active/--no-active',
    default=True,
    help=(
        "This flag indicates whether the attach command will use "
        "the chain that is referenced from the <proj>/chains/.active-chain "
        "to load information about known contracts or not."
    ),
)
@click.option(
    '--rpc',
    default="127.0.0.1:8545",
    metavar="<IP>:<PORT>",
    help=(
        "Set the RPC endpoint of the ethereum instance we are targeting. "
        "Default: 127.0.0.1:8545"
        ),
)
def attach(active, rpc):
    """
    Enter a python shell with contracts and blockchain client
    available.
    """
    project_dir = os.path.abspath(os.getcwd())
    contracts_meta = utils.load_contracts(project_dir)
    ipStr, port = utils.parse_ipv4_endpoint(rpc)
    client = Client(ipStr, port)

    context = {
        'contracts': package_contracts(contracts_meta),
        'client': client,
    }
    data_dir = None
    if active:
        data_dir = get_active_data_dir(project_dir)
        if os.path.islink(data_dir):
            setup_known_instances(context, data_dir)
        else:
            click.echo(click.style("No Valid Active Chain Data Directory Found!", fg="red"))

    def redeploy(contracts=[], record=True):
        return(deploy_set(
            context, client, project_dir, data_dir=data_dir,
            record=record, contracts_by_name=contracts
        ))

    context["redeploy"] = redeploy

    contract_names = ', '.join(sorted(contracts_meta.keys()))

    banner = textwrap.dedent(
        """
        Python: {python_version}

        Populus: v{populus_version}

        Project Path: {project_dir}

        contracts  -> Contract classes
        client     -> Blockchain client ({client_type})
        redeploy   -> Method to re-deploy project contracts
                      Example:
                        deployed_cts = redeploy()
                        deployed_cts = redeploy(record = False)
                        deployed_cts = redeploy(contracts = ["Example"])

        Contracts: {contracts}
        Check contracts.<type>.known for deployed contracts.

        """
    ).format(
        python_version=sys.version.partition('\n')[0],
        populus_version=populus.__version__,
        project_dir=project_dir,
        client_type="json-rpc",
        contracts=click.wrap_text(
            contract_names, initial_indent='', subsequent_indent=' ' * 4,
        ),
    ).strip()

    if is_ipython:
        shell = InteractiveConsole(user_ns=context)
    else:
        shell = InteractiveConsole(context)

    # Start the active directory link observer
    event_handler = ActiveDataDirChangedEventHandler(
        project_dir=project_dir,
        context=context,
    )
    observer = get_active_dir_observer(project_dir, event_handler)

    observer.start()
    shell.interact(banner)
    observer.stop()
    observer.join()
