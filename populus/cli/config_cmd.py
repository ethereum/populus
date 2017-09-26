from __future__ import absolute_import

import logging
import warnings

import click

from eth_utils import (
    to_tuple,
)

from populus.config.defaults import (
    LATEST_VERSION,
)
from populus.config.upgrade import (
    upgrade_config,
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


@config_cmd.command('set')
@click.pass_context
@click.argument(
    'key_value_pairs',
    callback=validate_key_value,
    nargs=-1,
)
def config_set(ctx, key_value_pairs):
    """
    Sets the provided key/value pairs in the project config.
    """
    warn_msg = 'Next release of populus will simplify configs. Config set will be dropped for simple config file edit'  # noqa: E501
    warnings.warn(warn_msg, DeprecationWarning)
    logger = logging.getLogger('populus.cli.config.set')
    project = ctx.obj['PROJECT']
    for key, value in key_value_pairs:
        is_already_present = key in project.config
        project.config[key] = value
        logger.info("{0}: {1} ({2})".format(
            key,
            value,
            'updated' if is_already_present else 'added',
        ))
    project.write_config()


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


@config_cmd.command('delete')
@click.pass_context
@click.argument(
    'keys',
    nargs=-1,
)
def config_delete(ctx, keys):
    """
    Deletes the provided key/value pairs from the project config.
    """
    warn_msg = "Next release of populus will simplify configs. Config delete will be dropped for simple config file edit"  # noqa: E501
    warnings.warn(warn_msg, DeprecationWarning)
    logger = logging.getLogger('populus.cli.config.delete')
    project = ctx.obj['PROJECT']
    for key in keys:
        try:
            logger.info("{0}: {1} (deleted)".format(key, project.config[key]))
            del project.config[key]
        except KeyError:
            logger.error("KeyError: {0}".format(key), err=True)
    project.write_config()


@config_cmd.command('upgrade')
@click.pass_context
@click.option(
    '-t',
    '--to-version',
    'to_version',
    default=LATEST_VERSION,
)
def config_upgrade(ctx, to_version):
    """
    Upgrades the current populus config file to the specifed version.
    """
    logger = logging.getLogger('populus.cli.config.upgrade')
    project = ctx.obj['PROJECT']

    from_version = project.config['version']
    if from_version == LATEST_VERSION:
        logger.info("Already at latest version: v{0}".format(from_version))
        return

    upgraded_config = upgrade_config(project.config, to_version=to_version)
    logger.info(
        "Upgraded config from v{0} -> v{1}".format(from_version, to_version)
    )
    project.config = upgraded_config
    config_file_path = project.write_config()
    logger.info(
        "Wrote updated config to: `{0}`".format(config_file_path)
    )
