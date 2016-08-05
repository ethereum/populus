import os
import random

import gevent

import click

from populus.compilation import (
    get_contracts_dir,
    compile_and_write_contracts,
)
from populus.observers import (
    get_contracts_observer,
)
from solc.main import ALL_OUTPUT_VALUES

from .main import main


@main.command('compile')
@click.option(
    '--watch',
    '-w',
    is_flag=True,
    help="Watch contract source files and recompile on changes",
)
@click.option(
    '--optimize',
    '-o',
    default=True,
    is_flag=True,
    help="Enable compile time optimization",
)
@click.option(
    '--solc_overrides',
    '-s',
    type=click.Choice(ALL_OUTPUT_VALUES),
    help="Choose among the various output values which output you want",
    multiple=True
)
def compile_contracts(watch, optimize, solc_overrides):
    """
    Compile project contracts, storing their output in `./build/contracts.json`

    Call bare to compile all contracts or specify contract names or file paths
    to restrict to only compiling those contracts.

    Pass in a file path and a contract name separated by a colon(":") to
    specify only named contracts in the specified file.
    """
    project_dir = os.getcwd()
    output_values = [r for r in solc_overrides]
    click.echo("============ Compiling ==============")
    click.echo("> Loading contracts from: {0}".format(get_contracts_dir(project_dir)))
    result = compile_and_write_contracts(project_dir, optimize=optimize, output_values=output_values)
    contract_source_paths, compiled_sources, output_file_path = result

    click.echo("> Found {0} contract source files".format(
        len(contract_source_paths)
    ))
    for path in contract_source_paths:
        click.echo("- {0}".format(os.path.relpath(path)))
    click.echo("")
    click.echo("> Compiled {0} contracts".format(len(compiled_sources)))
    for contract_name in sorted(compiled_sources.keys()):
        click.echo("- {0}".format(contract_name))
    click.echo("")
    click.echo("> Outfile: {0}".format(output_file_path))

    if watch:
        # The path to watch
        click.echo("============ Watching ==============")

        observer = get_contracts_observer(project_dir, {'optimize': optimize})
        observer.start()
        try:
            while observer.is_alive():
                gevent.sleep(random.random())
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
