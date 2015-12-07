import os
import sys
import textwrap
import hashlib
from datetime import datetime

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
from populus.geth import (
    get_geth_data_dir,
    get_known_contracts,
)

from .main import main


def setup_known_instances(context, name):
    data_dir = get_geth_data_dir(os.getcwd(), name)
    # Attempt to load known contracts.
    knownCts = get_known_contracts(data_dir)
    for name in knownCts.keys():
        addrList = knownCts[name]
        # Latest Instances contains a list of the deployed contracts
        # for which the code matches with the current project
        # context's contract code. We use a sha512 hash to compare
        # the code of each. The idea here is to catch cases where the
        # user has updated their code but failed to redeploy, and
        # cases where new contract methods might attempt to be called
        # on old contract addresses
        latestInstances = []
        ctType = None
        try:
            ctType = getattr(context["contracts"], name)
        except AttributeError:
            click.echo("Failed to find contract `{0}` in project context: skipping".format(name))
            continue
        currCodeHash = hashlib.sha512(ctType._config.code).hexdigest()
        for data in addrList:
            if currCodeHash == data["codehash"]:
                inst = ctType(data["address"], context["client"])
                ts = datetime.strptime(data["ts"], "%Y-%m-%dT%H:%M:%S.%f")
                latestInstances.append((ts, inst))

        # Ok - latestInstances has all the instances of this
        # contract type whose code matches with what we expect
        # it to be. Now let's sort this list by the time
        # stamp
        latestInstances.sort(key=lambda r: r[0])
        setattr(ctType, "known", [x[1] for x in latestInstances])


@main.command()
@click.option(
    '--knownfrom',
    type=str,
    default=None,
    help=(
        "Name of the test chain that we are attaching to. This is an "
        "optional argument that can be used to help populate the "
        "user environment with contracts recorded by the `deploy` "
        "sub-command. This options is primarily intended to be "
        "used with test chains when using the populus workflow. If "
        "the passed chain has known contracts, it will "
        "select all known contracts for each contract type and confirm "
        "that the were deployed with latest contract code. These valid "
        "addresses will be sorted by latest time stamp, and then added "
        "as instances of their particular contract type into a list "
        "on the member attribute 'known' on that contract class."
    ),
)
def attach(knownfrom):
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

    if knownfrom is not None:
        setup_known_instances(context, knownfrom)

    contract_names = ', '.join(sorted(contracts_meta.keys()))

    banner = textwrap.dedent(
        """
        Python: {python_version}

        Populus: v{populus_version}

        Project Path: {project_dir}

        contracts  -> Contract classes
        client     -> Blockchain client ({client_type})

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
    shell.interact(banner)
