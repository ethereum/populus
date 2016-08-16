import click

from populus.project import (
    Project,
)


CONTEXT_SETTINGS = dict(
    # Support -h as a shortcut for --help
    help_option_names=['-h', '--help'],
)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--config',
    '-c',
    help=(
        "Specify a populus configuration file to be used.  No other "
        "configuration files will be loaded"
    ),
    type=click.File(),
    multiple=True,
)
@click.pass_context
def main(ctx, config):
    """
    Populus
    """
    project = Project(config)

    ctx.obj = {}
    ctx.obj['PROJECT'] = project
