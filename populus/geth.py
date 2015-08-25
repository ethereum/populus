import os
import re
import functools
import subprocess

from populus import utils


is_geth_available = functools.partial(utils.is_executable_available, 'geth')
is_nice_available = functools.partial(utils.is_executable_available, 'nice')


POPULUS_DIR = os.path.abspath(os.path.dirname(__file__))


def get_blockchains_dir(project_dir):
    return os.path.abspath(os.path.join(project_dir, 'chains'))


def get_geth_data_dir(project_dir, name):
    blockchains_dir = get_blockchains_dir(project_dir)
    return os.path.join(blockchains_dir, name)


def geth_wrapper(data_dir, cmd="geth", genesis_block=None, miner_threads='1',
                 extra_args=None, max_peers='0', network_id='123456',
                 no_discover=True, mine=False, nice=True):
    if nice and is_nice_available():
        command = ['nice', '-n', '20', cmd]
    else:
        command = [cmd]

    if genesis_block is None:
        genesis_block = os.path.join(POPULUS_DIR, 'genesis-test.json')
    command.extend((
        '--datadir', data_dir,
        '--minerthreads', miner_threads,
        '--maxpeers', max_peers,
        '--networkid', network_id,
    ))

    if no_discover:
        command.append('--nodiscover')

    if mine:
        command.append('--mine')

    if extra_args:
        command.extend(extra_args)

    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return command, proc


def get_geth_accounts(data_dir, **kwargs):
    """
    Returns all geth accounts as tuple of hex encoded strings

    >>> geth_accounts()
    ... ('0x...', '0x...')
    """
    command, proc = geth_wrapper(data_dir, extra_args=['account', 'list'], **kwargs)
    stdoutdata, stderrdata = proc.communicate()

    if proc.returncode:
        if "no keys in store" in stderrdata:
            return tuple()
        else:
            raise subprocess.CalledProcessError(1, ' '.join(command))
    accounts = parse_geth_accounts(stdoutdata)
    return accounts


account_regex = re.compile('\{([a-f0-9]{40})\}')


def parse_geth_accounts(raw_accounts_output):
    accounts = account_regex.findall(raw_accounts_output)
    return tuple('0x' + account for account in accounts)


def run_geth_node(data_dir, rpc_server=True, rpc_addr=None, rpc_port=None, **kwargs):
    extra_args = []

    if rpc_server:
        extra_args.append('--rpc')

    if rpc_addr is not None:
        extra_args.extend(('--rpcaddr', rpc_addr))

    if rpc_port is not None:
        extra_args.extend(('--rpcport', rpc_port))

    _, proc = geth_wrapper(data_dir, extra_args=extra_args, **kwargs)
    return proc
