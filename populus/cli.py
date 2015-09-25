import os
import time
import signal
import multiprocessing

import pytest

import click

from eth_rpc_client import Client

from populus import utils
from populus.compilation import (
    get_contracts_dir,
    compile_and_write_contracts,
)
from populus.observers import (
    get_contracts_observer,
    get_contracts_code_observer,
    get_static_assets_observer,
)
from populus.web import (
    get_flask_app,
    collect_static_assets,
    compile_js_contracts,
    get_html_dir,
    write_default_index_html_document,
    get_static_assets_dir,
)
from populus.geth import (
    get_geth_data_dir,
    get_geth_logfile_path,
    run_geth_node,
    ensure_account_exists,
    reset_chain,
)


@click.group()
def main():
    pass


@main.command()
def init():
    """
    Generate project layout with an example contract.
    """
    project_dir = os.getcwd()
    contracts_dir = get_contracts_dir(project_dir)
    if utils.ensure_path_exists(contracts_dir):
        click.echo("Created Directory: ./{0}".format(os.path.relpath(contracts_dir)))

    example_contract_path = os.path.join(contracts_dir, 'Example.sol')
    if not os.path.exists(example_contract_path):
        with open(example_contract_path, 'w') as example_contract_file:
            example_contract_file.write('contract Example {\n        function Example() {\n        }\n}\n')  # NOQA
        click.echo("Created Example Contract: ./{0}".format(os.path.relpath(example_contract_path)))  # NOQA

    tests_dir = os.path.join(project_dir, 'tests')
    if utils.ensure_path_exists(tests_dir):
        click.echo("Created Directory: ./{0}".format(os.path.relpath(tests_dir)))

    example_tests_path = os.path.join(tests_dir, 'test_example.py')
    if not os.path.exists(example_tests_path):
        with open(example_tests_path, 'w') as example_tests_file:
            example_tests_file.write('def test_it(deployed_contracts):\n    example = deployed_contracts.Example\n    assert example.address\n')  # NOQA
        click.echo("Created Example Tests: ./{0}".format(os.path.relpath(example_tests_path)))  # NOQA

    initialize_web_directories(project_dir)


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
    is_flag=True,
    help="Enable compile time optimization",
)
@click.argument('filters', nargs=-1)
def compile_contracts(watch, optimize, filters):
    """
    Compile project contracts, storing their output in `./build/contracts.json`

    Call bare to compile all contracts or specify contract names or file paths
    to restrict to only compiling those contracts.

    Pass in a file path and a contract name separated by a colon(":") to
    specify only named contracts in the specified file.
    """
    project_dir = os.getcwd()

    click.echo("============ Compiling ==============")
    click.echo("> Loading contracts from: {0}".format(get_contracts_dir(project_dir)))

    result = compile_and_write_contracts(project_dir, *filters, optimize=optimize)
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

    if watch:
        # The path to watch
        click.echo("============ Watching ==============")

        observer = get_contracts_observer(project_dir, filters, {'optimize': optimize})
        observer.start()
        try:
            while observer.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


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
    Test contracts (wrapper around py.test)
    """
    pytest.main(os.path.join(os.getcwd(), 'tests'))


@main.group()
def web():
    """
    HTML/CSS/JS tooling.
    """
    pass


def initialize_web_directories(project_dir):
    html_dir = get_html_dir(project_dir)
    if utils.ensure_path_exists(html_dir):
        click.echo("Created Directory: ./{0}".format(os.path.relpath(html_dir)))

    html_index_path = os.path.join(html_dir, 'index.html')
    if not os.path.exists(html_index_path):
        write_default_index_html_document(html_index_path)
        click.echo("Created HTML Index File: ./{0}".format(os.path.relpath(html_index_path)))

    static_assets_dir = get_static_assets_dir(project_dir)
    if utils.ensure_path_exists(static_assets_dir):
        click.echo("Created Directory: ./{0}".format(os.path.relpath(static_assets_dir)))


@web.command('init')
def web_init():
    project_dir = os.getcwd()
    initialize_web_directories(project_dir)


@web.command('runserver')
@click.option('--debug/--no-debug', default=True)
def web_runserver(debug):
    """
    Run the development server.
    """
    project_dir = os.getcwd()
    # Do initial setup
    click.echo("Compiling contracts...")
    compile_and_write_contracts(project_dir)
    click.echo("Compiling contracts.js...")
    compile_js_contracts(project_dir)
    click.echo("Collectind static assets...")
    collect_static_assets(project_dir)

    all_threads = []

    # Contract Builder Thread
    contracts_observer_thread = get_contracts_observer(project_dir)
    contracts_observer_thread.daemon = True

    # Contract JS Builder Thread
    contracts_code_observer_thread = get_contracts_code_observer(project_dir)
    contracts_code_observer_thread.daemon = True

    # Assets Collector Thread
    static_assets_observer_thread = get_static_assets_observer(project_dir)
    static_assets_observer_thread.daemon = True

    # Webserver Thread
    flask_app = get_flask_app(project_dir)
    webserver_thread = multiprocessing.Process(
        target=flask_app.run,
        kwargs={'use_reloader': False, 'debug': debug},
    )
    webserver_thread.daemon = True

    # Start all the threads
    contracts_observer_thread.start()
    contracts_code_observer_thread.start()
    static_assets_observer_thread.start()
    webserver_thread.start()

    try:
        all_threads = (
            contracts_observer_thread,
            contracts_code_observer_thread,
            static_assets_observer_thread,
            webserver_thread,
        )
        while any(t.is_alive() for t in all_threads):
            if not all(t.is_alive() for t in all_threads):
                raise click.Abort("Some threads died!")
            time.sleep(1)
    except KeyboardInterrupt:
        for t in all_threads:
            if hasattr(t, 'stop'):
                t.stop()
            elif hasattr(t, 'terminate'):
                t.terminate()
            else:
                raise ValueError("wat")
        for t in all_threads:
            t.join()


@web.command('collect')
def web_collect():
    """
    Compile the contracts.js file and collect static assets.
    """
    compile_js_contracts(os.getcwd())
    collect_static_assets(os.getcwd())


@main.group()
def chain():
    """
    Wrapper around `geth`.
    """
    pass


@chain.command('reset')
@click.argument('name', nargs=1, default="default")
@click.option('--confirm/--no-confirm', default=True)
def chain_reset(name, confirm):
    """
    Reset a test chain
    """
    data_dir = get_geth_data_dir(os.getcwd(), name)
    if confirm and not click.confirm("Are you sure you want to reset blockchain '{0}': {1}".format(name, data_dir)):  # NOQA
        raise click.Abort()
    reset_chain(data_dir)


@chain.command('run')
@click.argument('name', nargs=1, default="default")
@click.option('--mine/--no-mine', default=True)
def chain_run(name, mine):
    """
    Run a geth node.
    """
    data_dir = get_geth_data_dir(os.getcwd(), name)
    logfile_path = get_geth_logfile_path(data_dir)

    ensure_account_exists(data_dir)

    command, proc = run_geth_node(data_dir, mine=mine, logfile=logfile_path)

    click.echo("Running: '{0}'".format(' '.join(command)))

    try:
        while True:
            out_line = proc.get_stdout_nowait()
            if out_line:
                click.echo(out_line, nl=False)

            err_line = proc.get_stderr_nowait()
            if err_line:
                click.echo(err_line, nl=False)

            if err_line is None and out_line is None:
                time.sleep(0.2)
    except KeyboardInterrupt:
        try:
            proc.send_signal(signal.SIGINT)
            # Give the subprocess a SIGINT and give it a few seconds to
            # cleanup.
            utils.wait_for_popen(proc)
            while not proc.stdout_queue.empty() or not proc.stderr_queue.empty():
                out_line = proc.get_stdout_nowait()
                if out_line:
                    click.echo(out_line, nl=False)

                err_line = proc.get_stderr_nowait()
                if err_line:
                    click.echo(err_line, nl=False)
        except:
            # Try a harder termination.
            proc.terminate()
            utils.wait_for_popen(proc, 2)
    if proc.poll() is None:
        # Force it to kill if it hasn't exited already.
        proc.kill()
    if proc.returncode:
        raise click.ClickException("Error shutting down geth process.")
