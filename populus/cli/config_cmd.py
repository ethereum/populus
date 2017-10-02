from __future__ import absolute_import

import logging

import click

from eth_utils import (
    to_tuple,
)

from .main import main


@main.group('config')
@click.pass_context
def config_cmd(ctx):
    """
    Manage and run ethereum blockchains.
    """
    pass


@config_cmd.command('list')
@click.pass_context
def config_list(ctx):
    """
    Prints the project configuration out to the terminal
    """
    logger = logging.getLogger('populus.cli.config.list')

    project = ctx.obj['PROJECT']
    for key, value in project.config.items(flatten=True):
        logger.info("{0}: {1}".format(key, value))


@to_tuple
def validate_key_value(ctx, value):
    for kv in value:
        key, _, value = kv.partition(':')
        if not key or not value:
            raise click.BadParameter(
                "Config values must be set using the format '<key>:<value>'"
            )
        yield key, value


@config_cmd.command('get')
@click.pass_context
@click.argument(
    'keys',
    nargs=-1,
)
def config_get(ctx, keys):
    """
    Gets the provided key/value pairs from the project config.
    """
    logger = logging.getLogger('populus.cli.config.get')
    project = ctx.obj['PROJECT']
    for key in keys:
        try:
            logger.info("{0}: {1}".format(key, project.config[key]))
        except KeyError:
            logger.error("KeyError: {0}".format(key), err=True)
