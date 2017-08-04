from __future__ import absolute_import

import logging

import click


class ClickLogHandler(logging.Handler):
    def handle(self, record):
        click.echo(self.format(record))

    def handleError(self, record):
        click.echo(self.format(record), err=True)


def get_logger_with_click_handler(name, level=None):
    if level is None:
        level = logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not any(isinstance(h, ClickLogHandler) for h in logger.handlers):
        logger.addHandler(ClickLogHandler())

    return logger
