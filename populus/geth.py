import os
import copy
import re
import functools
import subprocess
from threading import Thread
from Queue import Queue, Empty
import json

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
    data_dir = os.path.join(blockchains_dir, name)
    utils.ensure_path_exists(data_dir)
    return data_dir


def enqueue_stream(stream, queue):
    """
    Synchronously reads the output from a stream (stdout, stderr) and puts it
    onto the queue to be read.
    """
    for line in iter(stream.readline, b''):
        queue.put(line)


class PopenWrapper(subprocess.Popen):
    _locked = False

    def __init__(self, args, bufsize='1', stdin=subprocess.PIPE,
                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs):
        super(PopenWrapper, self).__init__(args, bufsize=bufsize, stdin=stdin,
                                           stdout=stdout, stderr=stderr,
                                           **kwargs)
        self.stdout_queue = Queue()
        self.stdout_thread = Thread(
            target=enqueue_stream,
            args=(self.stdout, self.stdout_queue),
        )
        self.stdout_thread.daemon = True
        self.stdout_thread.start()

        self.stderr_queue = Queue()
        self.stderr_thread = Thread(
            target=enqueue_stream,
            args=(self.stderr, self.stderr_queue),
        )
        self.stderr_thread.daemon = True
        self.stderr_thread.start()

    def get_stdout_nowait(self):
        try:
            return self.stdout_queue.get_nowait()
        except Empty:
            return None

    def get_stderr_nowait(self):
        try:
            return self.stderr_queue.get_nowait()
        except Empty:
            return None

    _output_generator = None

    def get_output_nowait(self):
        if self._output_generator is None:
            def output_generator():
                while True:
                    yield self.get_stdout_nowait()
                    yield self.get_stderr_nowait()
            self._output_generator = output_generator()
        return self._output_generator.next()

    def communicate(self, *args, **kwargs):
        raise ValueError("Cannot communicate with a PopenWrapper")


DEFAULT_PW_PATH = os.path.join(POPULUS_DIR, 'default_blockchain_password')


def geth_wrapper(data_dir, popen_class=subprocess.Popen, cmd="geth",
                 genesis_block=None, miner_threads='1', extra_args=None,
                 max_peers='0', network_id='123456', no_discover=True,
                 mine=False, nice=True, unlock='0', password=DEFAULT_PW_PATH,
                 port=None):
    if nice and is_nice_available():
        command = ['nice', '-n', '20', cmd]
    else:
        command = [cmd]

    if genesis_block is None:
        genesis_block = get_genesis_block_path(data_dir)
        if not os.path.exists(genesis_block):
            genesis_block = os.path.join(POPULUS_DIR, 'genesis-test.json')

    if port is None:
        port = utils.get_open_port()

    command.extend((
        '--genesis', genesis_block,
        '--datadir', data_dir,
        '--maxpeers', max_peers,
        '--networkid', network_id,
        '--port', port,
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

    proc = popen_class(
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


default_genesis_data = {
    "nonce": "0xdeadbeefdeadbeef",
    "timestamp": "0x0",
    "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
    "extraData": "0x686f727365",
    "gasLimit": "0x80000000000000",
    "difficulty": "0x400",
    "mixhash": "0x0000000000000000000000000000000000000000000000000000000000000000",
    "coinbase": "0x3333333333333333333333333333333333333333",
    "alloc": {}
}


def get_genesis_block_path(data_dir):
    return os.path.join(data_dir, 'genesis-block.json')


def ensure_account_exists(data_dir):
    accounts = get_geth_accounts(data_dir)
    if not accounts:
        account = create_geth_account(data_dir)
        genesis_block_path = get_genesis_block_path(data_dir)
        if not os.path.exists(genesis_block_path):
            genesis_data = copy.deepcopy(default_genesis_data)
            genesis_data['alloc'][account] = {
                "balance": "1000000000000000000000000000",  # 1,000,000,000 ether
            }
            with open(genesis_block_path, 'w') as genesis_block_file:
                genesis_block_file.write(json.dumps(genesis_data))
    else:
        account = accounts[0]
    return account


account_regex = re.compile('\{([a-f0-9]{40})\}')


def parse_geth_accounts(raw_accounts_output):
    accounts = account_regex.findall(raw_accounts_output)
    return tuple('0x' + account for account in accounts)


def run_geth_node(data_dir, rpc_server=True, rpc_addr=None, rpc_port=None,
                  mine=True, **kwargs):
    extra_args = []

    if rpc_server:
        extra_args.append('--rpc')

        if rpc_addr is not None:
            extra_args.extend(('--rpcaddr', rpc_addr))

        if rpc_port is not None:
            extra_args.extend(('--rpcport', rpc_port))

    command, proc = geth_wrapper(data_dir, popen_class=PopenWrapper,
                                 extra_args=extra_args, mine=mine, **kwargs)
    return command, proc


def reset_chain(data_dir):
    blockchain_dir = os.path.join(data_dir, 'chaindata')
    utils.remove_dir_if_exists(blockchain_dir)

    dapp_dir = os.path.join(data_dir, 'dapp')
    utils.remove_dir_if_exists(dapp_dir)

    nodekey_path = os.path.join(data_dir, 'nodekey')
    utils.remove_file_if_exists(nodekey_path)

    geth_ipc_path = os.path.join(data_dir, 'geth.ipc')
    utils.remove_file_if_exists(geth_ipc_path)
