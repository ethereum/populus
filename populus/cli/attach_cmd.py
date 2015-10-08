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

import populus
from populus import utils
from populus.contracts import (
    package_contracts,
)

from .main import main


@main.command()
def attach():
    """
    Enter a python shell with contracts and blockchain client
    available.
    """
    project_dir = os.path.abspath(os.getcwd())
    contracts_meta = utils.load_contracts(project_dir)

    context = {
        'contracts': package_contracts(contracts_meta),
        'client': Client('127.0.0.1', '8545'),
    }

    contract_names = ', '.join(sorted(contracts_meta.keys()))

    banner = textwrap.dedent(
        """
        Python: {python_version}

        Populus: v{populus_version}

        Project Path: {project_dir}

        contracts  -> Contract classes
        client     -> Blockchain client ({client_type})

        Contracts: {contracts}
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
    shell.interact(banner)
