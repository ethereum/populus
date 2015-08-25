import os
import shutil
import re
import functools
import subprocess

from populus import utils


is_geth_available = functools.partial(utils.is_executable_available, 'geth')
is_nice_available = functools.partial(utils.is_executable_available, 'nice')


POPULUS_DIR = os.path.abspath(os.path.dirname(__file__))


def get_blockchains_dir(project_dir):
    blockchains_dir = os.path.abspath(os.path.join(project_dir, 'chains'))
    utils.ensure_path_exists(blockchains_dir)
    return blockchains_dir


def get_geth_data_dir(project_dir, name):
    blockchains_dir = get_blockchains_dir(project_dir)
    return os.path.join(blockchains_dir, name)


DEFAULT_PW_PATH = os.path.join(POPULUS_DIR, 'default_blockchain_password')


def geth_wrapper(data_dir, cmd="geth", genesis_block=None, miner_threads='1',
                 extra_args=None, max_peers='0', network_id='123456',
                 no_discover=True, mine=False, nice=True, unlock='0',
                 password=DEFAULT_PW_PATH):
    if nice and is_nice_available():
        command = ['nice', '-n', '20', cmd]
    else:
        command = [cmd]

    if genesis_block is None:
        genesis_block = os.path.join(POPULUS_DIR, 'genesis-test.json')
    command.extend((
        '--genesis', genesis_block,
        '--datadir', data_dir,
        '--maxpeers', max_peers,
        '--networkid', network_id,
    ))

    if miner_threads is not None:
        command.extend(('--minerthreads', miner_threads))

    if unlock is not None:
        command.extend((
            '--unlock', unlock,
        ))

    if password is not None:
        command.extend((
            '--password', password,
        ))

    if no_discover:
        command.append('--nodiscover')

    if mine:
        if unlock is None:
            raise ValueError("Cannot mine without an unlocked account")
        command.append('--mine')

    if extra_args:
        command.extend(extra_args)

    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
    )
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


def create_geth_account(data_dir, **kwargs):
    command, proc = geth_wrapper(data_dir, extra_args=['account', 'new'], **kwargs)
    stdoutdata, stderrdata = proc.communicate()

    if proc.returncode:
        raise subprocess.CalledProcessError(1, ' '.join(command))

    match = account_regex.search(stdoutdata)
    if not match:
        raise ValueError("No address found in output: '{0}'".format(stdoutdata))

    return '0x' + match.groups()[0]


def ensure_account_exists(data_dir):
    if not get_geth_accounts(data_dir):
        create_geth_account(data_dir)


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

    command, proc = geth_wrapper(data_dir, extra_args=extra_args, **kwargs)
    return command, proc


def reset_chain(data_dir):
    blockchain_dir = os.path.join(data_dir, 'chaindata')
    if os.path.exists(blockchain_dir):
        shutil.rmtree(blockchain_dir)
