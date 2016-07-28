from __future__ import absolute_import

import click

from watchdog.observers.polling import (
    PollingObserver,
)
from watchdog.events import FileSystemEventHandler

from .utils.filesystem import (
    get_blockchains_dir,
    get_contracts_dir,
)
from populus.compilation import (
    compile_and_write_contracts,
)


def get_active_dir_observer(project_dir, event_handler):
    """ Setup a polling observer on the project's
        blockchains directory. This directory contains the
        .active-chain symlink which is watched for.
    """
    # TODO:
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


def get_contracts_observer(project_dir,
                           compiler_kwargs=None):
    if compiler_kwargs is None:
        compiler_kwargs = {}
    contracts_dir = get_contracts_dir(project_dir)

    event_handler = ContractSourceChangedEventHandler(
        project_dir=project_dir,
        compiler_kwargs=compiler_kwargs,
    )
    observer = PollingObserver()
    observer.schedule(event_handler, contracts_dir, recursive=True)
    return observer
