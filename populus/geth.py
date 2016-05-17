from Queue import Queue, Empty
from threading import Thread
import copy
import datetime
import functools
import time
import json
import os
import re
import subprocess
import hashlib
import tempfile

from populus import utils


is_geth_available = functools.partial(utils.is_executable_available, 'geth')
is_nice_available = functools.partial(utils.is_executable_available, 'nice')


POPULUS_DIR = os.path.abspath(os.path.dirname(__file__))
KNOWN_CONTRACTS_FILE = "known_contracts.json"
ACTIVE_CHAIN_SYMLINK = ".active-chain"


def get_blockchains_dir(project_dir):
    blockchains_dir = os.path.abspath(os.path.join(project_dir, 'chains'))
    utils.ensure_path_exists(blockchains_dir)
    return blockchains_dir


def get_geth_data_dir(project_dir, name):
    blockchains_dir = get_blockchains_dir(project_dir)
    data_dir = os.path.abspath(os.path.join(blockchains_dir, name))
    utils.ensure_path_exists(data_dir)
    return data_dir


def get_active_data_dir(project_dir):
    """ Given a project directory, this function creates the
        file path string for the active chain symlink.
    """
    bc_dir = get_blockchains_dir(project_dir)
    active_dir = os.path.abspath(os.path.join(bc_dir, ACTIVE_CHAIN_SYMLINK))
    return active_dir


def set_active_data_dir(project_dir, name):
    """ Set which ethereum chain directory is the
        active chain. This basically just creates a new
        symlink pointed at the active chain.
    """
    data_dir = get_geth_data_dir(project_dir, name)
    active_dir = get_active_data_dir(project_dir)
    if os.path.islink(active_dir):
        os.unlink(active_dir)
    os.symlink(data_dir, active_dir)


def get_geth_logfile_path(data_dir, logfile_name_fmt="geth-{0}.log"):
    logfile_name = logfile_name_fmt.format(
        datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),
    )
    log_dir = os.path.join(data_dir, 'logs')
    utils.ensure_path_exists(log_dir)
    logfile_path = os.path.abspath(os.path.join(log_dir, logfile_name))
    return logfile_path


def enqueue_stream(stream, queue, logfile=None):
    """
    Synchronously reads the output from a stream (stdout, stderr) and puts it
    onto the queue to be read.
    """
    for line in iter(stream.readline, b''):
        queue.put(line)
        if logfile:
            logfile.write(line)
            logfile.flush()
    if logfile:
        try:
            logfile.close()
        except ValueError:
            pass


class PopenWrapper(subprocess.Popen):
    _locked = False

    def __init__(self, args, bufsize='1', stdin=subprocess.PIPE,
                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs):
        super(PopenWrapper, self).__init__(args, bufsize=bufsize, stdin=stdin,
                                           stdout=stdout, stderr=stderr,
                                           **kwargs)
        if "--logfile" in args:
            logfile_path = args[args.index("--logfile") + 1]
            logfile = open(logfile_path, 'a')
        else:
            logfile = None
        self.stdout_queue = Queue()
        self.stdout_thread = Thread(
            target=enqueue_stream,
            args=(self.stdout, self.stdout_queue, logfile),
        )
        self.stdout_thread.daemon = True
        self.stdout_thread.start()

        self.stderr_queue = Queue()
        self.stderr_thread = Thread(
            target=enqueue_stream,
            args=(self.stderr, self.stderr_queue, logfile),
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
                 port=None, verbosity=None, logfile=None, whisper=True,
                 ipcpath=None):
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

    if ipcpath is None:
        ipcpath = tempfile.NamedTemporaryFile().name

    command.extend((
        '--genesis', genesis_block,
        '--datadir', data_dir,
        '--maxpeers', max_peers,
        '--networkid', network_id,
        '--port', port,
        '--ipcpath', ipcpath,
    ))

    if whisper:
        command.append('--shh')
        command.extend(('--rpcapi', 'db,eth,net,web3,shh'))

    if miner_threads is not None:
        command.extend(('--minerthreads', miner_threads))

    if verbosity is not None:
        command.extend((
            '--verbosity', verbosity,
        ))

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
    "gasLimit": "0x2fefd8",
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
    extra_args = kwargs.pop('extra_args', [])

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
    # Reset the known contracts so that we don't try to
    # reference contract addresses that don't exist.
    known_contracts_path = os.path.join(data_dir, KNOWN_CONTRACTS_FILE)
    utils.remove_file_if_exists(known_contracts_path)


def get_known_contracts(data_dir):
    """ Retrieve the known contract files from the geth data
        directory and return as a python dict.
    """
    knownCts = {}
    knownCtsFile = os.path.join(data_dir, KNOWN_CONTRACTS_FILE)
    try:
        with open(knownCtsFile, "rb") as f:
            knownCts = json.load(f)
    except IOError:
        # Indicates that we couldn't open the file - it either
        # doesn't exist or we don't have permissions
        pass
    return(knownCts)


def add_to_known_contracts(deployed_contracts, data_dir):
    """ This method updates the known_contracts.json
        with the results of the deployed contracts.
        This can be useful when testing and namereg is
        either not available or not worth the hassel.
        @param deployed_contracts dict of deployed contract
            data indexed by the contract name.
        @param data_dir directory of the ethereum chain
            data.
    """
    knownCts = get_known_contracts(data_dir)

    ts = datetime.datetime.now().isoformat()
    # Now we will add to our known contracts
    for name, contract in deployed_contracts:
        codeHash = hashlib.sha512(contract._config.code).hexdigest()
        newCt = {
            "ts": ts,
            "address": contract._meta.address,
            "codehash": codeHash,
        }

        if name not in knownCts:
            knownCts[name] = []

        knownCts[name].append(newCt)

    # Write out the new known contracts file
    knownCtsFile = os.path.join(data_dir, KNOWN_CONTRACTS_FILE)
    with open(knownCtsFile, "wb") as f:
        json.dump(knownCts, f)


def wait_for_geth_to_start(proc, max_wait=10):
    start = time.time()
    while time.time() < start + max_wait:
        output = []
        line = proc.get_output_nowait()
        if line:
            output.append(line)

        if line is None:
            continue
        if 'Starting mining operation' in line:
            break
        elif "Still generating DAG" in line:
            print(line[line.index("Still generating DAG"):])
        elif line.startswith('Fatal:'):
            utils.kill_proc(proc)
            raise ValueError(
                "Geth Errored while starting\nerror: {0}\n\nFull Output{1}".format(
                    line, ''.join(output),
                )
            )
    else:
        utils.kill_proc(proc)
        raise ValueError("Geth process never started\n\n{0}".format(''.join(output)))
