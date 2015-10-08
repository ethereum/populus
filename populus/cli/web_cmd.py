import os
import time
import multiprocessing

import click

from populus import utils
from populus.compilation import (
    compile_and_write_contracts,
)
from populus.web import (
    get_flask_app,
    collect_static_assets,
    compile_js_contracts,
    get_html_dir,
    write_default_index_html_document,
    get_static_assets_dir,
)
from populus.observers import (
    get_contracts_observer,
    get_contracts_code_observer,
    get_static_assets_observer,
)

from .main import main


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
