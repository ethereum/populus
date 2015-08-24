import os
import re
import functools
import subprocess

from populus import utils


is_geth_available = functools.partial(utils.is_executable_available, 'geth')


POPULUS_DIR = os.path.abspath(os.path.dirname(__file__))


def get_blockchains_dir(project_dir):
    return os.path.abspath(os.path.join(project_dir, 'chains'))


def get_geth_data_dir(project_dir, name):
    blockchains_dir = get_blockchains_dir(project_dir)
    return os.path.join(blockchains_dir, name)


def geth_wrapper(data_dir, cmd="geth", genesis_block=None, extra_args=None):
    if genesis_block is None:
        genesis_block = os.path.join(POPULUS_DIR, 'genesis-test.json')
    command = [cmd, '--datadir', data_dir]

    if extra_args:
        command.extend(extra_args)

    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return command, proc


def get_geth_accounts(*args, **kwargs):
    """
    Returns all geth accounts as tuple of hex encoded strings

    >>> geth_accounts()
    ... ('0x...', '0x...')
    """
    extra_args = kwargs.get('extra_args', [])
    extra_args.extend(('account', 'list'))

    kwargs['extra_args'] = extra_args

    command, proc = geth_wrapper(*args, **kwargs)
    stdoutdata, stderrdata = proc.communicate()

    if proc.returncode:
        if "no keys in store" in stderrdata:
            raise ValueError("No accounts")
        else:
            raise subprocess.CalledProcessError(1, ' '.join(command))
    accounts = parse_geth_accounts(stdoutdata)
    return accounts


account_regex = re.compile('\{([a-f0-9]{40})\}')


def parse_geth_accounts(raw_accounts_output):
    accounts = account_regex.findall(raw_accounts_output)
    return tuple('0x' + account for account in accounts)
