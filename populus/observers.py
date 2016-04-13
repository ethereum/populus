import os

import click

from watchdog.observers.polling import (
    PollingObserver,
)
from watchdog.events import FileSystemEventHandler

from populus import utils
from populus.web import (
    get_contracts_js_path,
    get_static_assets_dir,
    compile_js_contracts,
    collect_static_assets,
    project_has_assets,
)
from populus.compilation import (
    compile_and_write_contracts,
    get_project_libraries_dir,
    get_compiled_contract_destination_path,
)
from populus.geth import (
    get_blockchains_dir,
)


def get_active_dir_observer(project_dir, event_handler):
    """ Setup a polling observer on the project's
        blockchains directory. This directory contains the
        .active-chain symlink which is watched for.
    """
    bchain = get_blockchains_dir(project_dir)
    observer = PollingObserver()
    observer.schedule(event_handler, bchain, recursive=False)
    return observer


class ContractSourceChangedEventHandler(FileSystemEventHandler):
    """
    > http://pythonhosted.org/watchdog/api.html#watchdog.events.FileSystemEventHandler
    """
    def __init__(self, *args, **kwargs):
        self.project_dir = kwargs.pop('project_dir')
        self.contract_filters = kwargs.pop('contract_filters')
        self.compiler_kwargs = kwargs.pop('compiler_kwargs')

    def on_any_event(self, event):
        click.echo("============ Detected Change ==============")
        click.echo("> {0} => {1}".format(event.event_type, event.src_path))
        click.echo("> recompiling...")
        compile_and_write_contracts(
            self.project_dir,
            *self.contract_filters,
            **self.compiler_kwargs
        )
        click.echo("> watching...")


def get_contracts_observer(project_dir, contract_filters=None, compiler_kwargs=None):
    if contract_filters is None:
        contract_filters = []
    if compiler_kwargs is None:
        compiler_kwargs = {}
    contracts_dir = utils.get_contracts_dir(project_dir)
    libraries_dir = get_project_libraries_dir(project_dir)

    event_handler = ContractSourceChangedEventHandler(
        project_dir=project_dir,
        contract_filters=contract_filters,
        compiler_kwargs=compiler_kwargs,
    )
    observer = PollingObserver()
    observer.schedule(event_handler, contracts_dir, recursive=True)
    if os.path.exists(libraries_dir):
        observer.schedule(event_handler, libraries_dir, recursive=True)
    return observer


class ContractCodeChangedEventHandler(FileSystemEventHandler):
    def __init__(self, *args, **kwargs):
        self.project_dir = kwargs.pop('project_dir')

    def on_any_event(self, event):
        is_contracts_json_file = os.path.samefile(
            event.src_path,
            get_compiled_contract_destination_path(self.project_dir),
        )
        if not is_contracts_json_file:
            return

        click.echo("============ Detected Change ==============")
        click.echo("> {0} => {1}".format(event.event_type, event.src_path))
        click.echo("> Recreating 'contracts.js' ...")
        compile_js_contracts(self.project_dir)
        click.echo("> watching...")


def get_contracts_code_observer(project_dir):
    observer = PollingObserver()

    build_path = utils.get_build_dir(project_dir)
    event_handler = ContractCodeChangedEventHandler(project_dir=project_dir)
    observer.schedule(event_handler, build_path, recursive=False)

    return observer


class ContractsJSChangedEventHandler(FileSystemEventHandler):
    def __init__(self, *args, **kwargs):
        self.project_dir = kwargs.pop('project_dir')

    def on_any_event(self, event):
        is_contracts_js_file = os.path.samefile(
            event.src_path,
            get_contracts_js_path(self.project_dir),
        )
        if not is_contracts_js_file:
            click.echo("Ignoring: {0}".format(event.src_path))
            return

        click.echo("============ Detected Change ==============")
        click.echo("> {0} => {1}".format(event.event_type, event.src_path))
        click.echo("> Collecting Assets...")
        collect_static_assets(self.project_dir)
        click.echo("> watching...")


class AssetsChangedEventHandler(FileSystemEventHandler):
    def __init__(self, *args, **kwargs):
        self.project_dir = kwargs.pop('project_dir')

    def on_any_event(self, event):
        click.echo("============ Detected Change ==============")
        click.echo("> {0} => {1}".format(event.event_type, event.src_path))
        click.echo("> Collecting Assets...")
        collect_static_assets(self.project_dir)
        click.echo("> watching...")


def get_static_assets_observer(project_dir):
    build_path = utils.get_build_dir(project_dir)

    observer = PollingObserver()

    contracts_js_event_handler = ContractsJSChangedEventHandler(project_dir=project_dir)
    observer.schedule(contracts_js_event_handler, build_path, recursive=False)

    if project_has_assets(project_dir):
        assets_watch_path = get_static_assets_dir(project_dir)
        assets_event_handler = AssetsChangedEventHandler(project_dir=project_dir)
        observer.schedule(assets_event_handler, assets_watch_path, recursive=True)

    return observer
