import contextlib
import functools

import click

from testrpc import testrpc

from web3.providers.rpc import TestRPCProvider
from web3 import (
    Web3,
    RPCProvider,
    IPCProvider,
)

from geth import (
    DevGethProcess,
    InterceptedStreamsMixin,
    LoggingMixin,
)
from populus.utils.networking import (
    get_open_port,
    wait_for_http_connection,
)
from populus.utils.filesystem import (
    remove_file_if_exists,
    remove_dir_if_exists,
    get_blockchains_dir,
    tempdir,
)
from populus.utils.chains import (
    get_chaindata_dir,
    get_dapp_dir,
    get_nodekey_path,
    get_geth_ipc_path,
    get_geth_logfile_path,
)


def reset_chain(data_dir):
    chaindata_dir = get_chaindata_dir(data_dir)
    remove_dir_if_exists(chaindata_dir)

    dapp_dir = get_dapp_dir(data_dir)
    remove_dir_if_exists(dapp_dir)

    nodekey_path = get_nodekey_path(data_dir)
    remove_file_if_exists(nodekey_path)

    geth_ipc_path = get_geth_ipc_path(data_dir)
    remove_file_if_exists(geth_ipc_path)


class LocalChainGethProcess(InterceptedStreamsMixin, DevGethProcess):
    def __init__(self, *args, **kwargs):
        super(LocalChainGethProcess, self).__init__(*args, **kwargs)
        self.register_stdout_callback(click.echo)
        self.register_stderr_callback(functools.partial(click.echo, err=True))


@contextlib.contextmanager
def dev_geth_process(project_dir, chain_name):
    blockchains_dir = get_blockchains_dir(project_dir)
    local_chain_geth = LocalChainGethProcess(
        chain_name=chain_name,
        base_dir=blockchains_dir,
    )
    with local_chain_geth as geth:
        yield geth


class TestingGethProcess(LoggingMixin, DevGethProcess):
    pass


@contextlib.contextmanager
def testing_geth_process(project_dir, test_name):
    """A content manager to launch a new local Geth process for running tests.

    A fresh run in a new environment may need up to 10 minutes to
    generate DAG files.

    * See https://github.com/ethereum/wiki/wiki/Ethash-DAG

    * These are shared across all Ethereum nodes and live in
      ``$(HOME)/.ethash/`` folder

    Example:

    .. code-block:: python

        import pytest

        from web3 import Web3, RPCProvider
        from populus.chain import testing_geth_process


        @pytest.yield_fixture(scope="session")
        def web3(request, client_mode, client_credentials) -> Web3:
            '''A py.test fixture to get a Web3 interface to locally launched geth.

            This is session scoped fixture.
            Geth is launched only once during the beginning of the test run.

            Geth will have huge instant balance on its coinbase account.
            Geth will also mine our transactions on artificially
            low difficulty level.
            '''

            # Ramp up a local geth server, store blockchain files in the
            # current working directory
            with testing_geth_process(project_dir=os.getcwd(), test_name="test") as geth_proc:
                # Launched in port 8080
                web3 = Web3(RPCProvider(host="127.0.0.1", port=geth_proc.rpc_port))

                # Allow access to sendTransaction() to use coinbase balance
                # to deploy contracts. Password is from py-geth
                # default_blockchain_password file. Assume we don't
                # run tests for more than 9999 seconds
                coinbase = web3.eth.coinbase
                success = web3.personal.unlockAccount(
                    coinbase,
                    passphrase="this-is-not-a-secure-password",
                    duration=9999)

                assert success, "Could not unlock test geth coinbase account"

                yield web3


        @pytest.fixture(scope="session")
        def coinbase(web3) -> str:
            '''Get coinbase address of locally running geth.'''
            return web3.eth.coinbase


    :param project_dir: Directory where chain files and log files are stored
    :param test_name: An identifier that llows separatation log files for each test
    :return: :class:`populus.chain.TestingGethProcess`
    """
    with tempdir() as tmp_project_dir:
        blockchains_dir = get_blockchains_dir(tmp_project_dir)
        geth = TestingGethProcess(
            chain_name='tmp-chain',
            base_dir=blockchains_dir,
            stdout_logfile_path=get_geth_logfile_path(project_dir, test_name, 'stdout'),
            stderr_logfile_path=get_geth_logfile_path(project_dir, test_name, 'stderr'),
            overrides={'verbosity': '5', 'suffix_kwargs': ['--rpccorsdomain=*'], 'rpc_addr': 'localhost'},
        )
        with geth as running_geth:
            print('Geth Port:', running_geth.rpc_port)
            if running_geth.is_mining:
                running_geth.wait_for_dag(600)
            if running_geth.ipc_enabled:
                running_geth.wait_for_ipc(30)
            if running_geth.rpc_enabled:
                running_geth.wait_for_rpc(30)
            yield running_geth


class Chain(object):
    """
    Base class for how populus interacts with the blockchain.
    """
    project = None

    def __init__(self, project):
        self.project = project

    @property
    def web3(self):
        raise NotImplementedError("Must be implemented by subclasses")

    def __enter__(self):
        raise NotImplementedError("Must be implemented by subclasses")

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class TesterChain(Chain):
    provider = None
    port = None
    _web3 = None

    @property
    def web3(self):
        if self._web3 is None:
            if self.provider is None:
                raise ValueError(
                    "TesterChain instances must be running to access the web3 "
                    "object."
                )
            self._web3 = Web3(self.provider)
        return self._web3

    _running = False

    def __enter__(self):
        if self._running:
            raise ValueError("The TesterChain is already running")

        if self.port is None:
            self.port = get_open_port()

        self.provider = TestRPCProvider(port=self.port)

        testrpc.full_reset()
        testrpc.rpc_configure('eth_mining', False)
        testrpc.rpc_configure('eth_protocolVersion', '0x3f')
        testrpc.rpc_configure('net_version', 1)
        testrpc.evm_mine()

        wait_for_http_connection('127.0.0.1', self.port)
        self._running = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._running:
            raise ValueError("The TesterChain is not running")
        try:
            self.provider.server.shutdown()
            self.provider.server.server_close()
        finally:
            self._running = False
