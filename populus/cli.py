import os

import click

from populus import utils
from populus.compilation import (
    get_contracts_dir,
    compile_and_write_contracts,
)
from eth_rpc_client import Client


@click.group()
def main():
    pass


@main.command()
def compile():
    """
    Compile contracts.
    """
    project_dir = os.getcwd()

    click.echo("============ Compiling ==============")
    click.echo("> Loading contracts from: {0}".format(get_contracts_dir(project_dir)))

    result = compile_and_write_contracts(project_dir)
    contract_source_paths, compiled_sources, output_file_path = result

    click.echo("> Found {0} contract source files".format(len(contract_source_paths)))
    for path in contract_source_paths:
        click.echo("- {0}".format(os.path.basename(path)))
    click.echo("")
    click.echo("> Compiled {0} contracts".format(len(compiled_sources)))
    for contract_name in sorted(compiled_sources.keys()):
        click.echo("- {0}".format(contract_name))
    click.echo("")
    click.echo("> Outfile: {0}".format(output_file_path))


@main.command()
def deploy():
    """
    Deploy contracts.
    """
    contracts = utils.load_contracts(os.getcwd())
    client = Client('127.0.0.1', '8545')

    deployed_contracts = utils.deploy_contracts(client, contracts)

    name_padding = max(len(n) + 1 for n in deployed_contracts.keys())
    for name, info in deployed_contracts.items():
        click.echo("{name} @ {addr} via txn:{txn_hash}".format(
            name=name.ljust(name_padding),
            addr=(info.get('addr') or '<pending>').ljust(42),
            txn_hash=info['txn'].ljust(66),
        ))


@main.command()
def test():
    """
    Test contracts (wrapper around py-test)
    """
    import pytest
    pytest.main(os.path.join(os.getcwd(), 'tests'))


import time
from watchdog.observers.polling import (
    PollingObserver,
)
from watchdog.events import FileSystemEventHandler


class ContractChangedEventHandler(FileSystemEventHandler):
    """
    > http://pythonhosted.org/watchdog/api.html#watchdog.events.FileSystemEventHandler
    """
    def __init__(self, *args, **kwargs):
        self.project_dir = kwargs.pop('project_dir')

    def on_any_event(self, event):
        click.echo("============ Detected Change ==============")
        click.echo("> {0} => {1}".format(event.event_type, event.src_path))
        click.echo("> recompiling...")
        compile_and_write_contracts(self.project_dir)
        click.echo("> watching...")


@main.command()
def watch():
    """
    Watch the project contracts directory and recompile contracts when they
    change.
    """
    project_dir = os.getcwd()

    # Do initial compilation
    compile_and_write_contracts(project_dir)

    # The path to watch
    watch_path = utils.get_contracts_dir(project_dir)

    click.echo("============ Watching ==============")

    event_handler = ContractChangedEventHandler(project_dir=project_dir)
    observer = PollingObserver()
    observer.schedule(event_handler, watch_path, recursive=True)
    observer.start()
    try:
        while observer.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
