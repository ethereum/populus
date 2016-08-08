# Patch stdlib when using Populus.
# This should happen only when we are using populus as
# standanlone CLI application.
# https://github.com/pipermerriam/populus/issues/117
from gevent import monkey
monkey.patch_all()


from .main import main  # NOQA
from .chain_cmd import chain  # NOQA
from .compile_cmd import compile_contracts  # NOQA
from .deploy_cmd import deploy  # NOQA
from .init_cmd import init  # NOQA
