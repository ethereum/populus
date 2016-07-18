Testing
=======

.. contents:: :local:

Introduction
------------

The Populus framework provides some powerful utilities for testing your
contracts.  Testing in Populus is powered by the python testing framework
``py.test``.


Using py.test Plugin
--------------------

The Populus framework test fixtures are enabled for your
Python project either through py.test command line or
adding ``pytest_plugins`` global in your py.test test module.

Below is an example by adding ``pytest_plugins`` global:

.. code-block:: python

    #: We enable populus plugin for this test file
    #: http://doc.pytest.org/en/latest/plugins.html#requiring-loading-plugins-in-a-test-module-or-conftest-file
    pytest_plugins = "populus.plugin",


    def test_my_stuff(geth_coinbase, geth_node, rpc_client):
        pass


Configuration options are available in :class:`populus.plugin.PopulusConfig`.

Available Fixtures
------------------

See :mod:`populus.plugin` for available py.test fixtures.

Quick Contract Example
----------------------

Lets write a test for the following simple contract.

.. code-block::

    # ./contracts/Math.sol
    contract Math {
            function add(int a, int b) public returns (int result){
                result = a + b;
                return result;
            }

            function multiply7(int a) public returns (int result){
                result = a * 7;
                return result;
            }

            function return13() public returns (int result) {
                result = 13;
                return result;
            }
    }

Populus expects to find tests in the ``./tests`` directory of your project.
The only naming requirement of the test module is that it must begin with
``test_`` so that it will be found by ``pytest``.

.. code-block::

    # ./tests/test_math.py

    def test_contracts_has_correct_functions(contracts):
        assert contracts.Math
        # Check that our contract has all of the expected functions.
        assert hasattr(contracts.Math, 'add')
        assert hasattr(contracts.Math, 'multiply7')
        assert hasattr(contracts.Math, 'return13')


    def test_contract_function_return_values(eth_coinbase, deployed_contracts):
        math = deployed_contracts.Math
        # Check that our functions compute the expected values.
        assert math.add.call(11, 12, _from=eth_coinbase) == 23
        assert math.multiply7.call(11, _from=eth_coinbase) == 77
        assert math.return13.call(_from=eth_coinbase) == 13


The code above declares two tests, ``test_contracts_has_correct_functions`` and
``test_contract_function_return_values``.  We can run these tests with the
``test`` command.


.. code-block:: shell

    $ py.test -v
    =================================== test session starts ===================================
    platform darwin -- Python 2.7.10 -- py-1.4.30 -- pytest-2.7.2 -- /usr/bin/python
    rootdir: /path/to/my-project, inifile: pytest.ini
    plugins: populus, capturelog, timeout
    collected 2 items

    tests/test_example.py::test_contracts_has_correct_functions PASSED
    tests/test_example.py::test_contract_function_return_values PASSED

    ================================ 2 passed in 0.82 seconds =================================

In the tests above, you may have noticed the use of the pytest fixtures
``eth_coinbase``, ``contracts`` and ``deployed_contracts``.  These are provided
by ``populus`` to help make testing contracts easier.

Using ethtester client
----------------------

:mod:`populus.ethtester_client` provides facilities to run in-memory Ethereum blockchain.
It is not a normal Ethereum node, but one where you as the developer control the creation
of new blocks. Thus, you can make all tests deterministic as you always have full
control of transactions and balances in the test case.

.. note::

    ethtester doesn't have all capabilities of full Ethereum RPC service, like filters.

Here is a Python 3 flavored example how to use ethtester to deploy a contract
taht you can stress in your tests:

.. code-block:: python


    import binascii
    import pytest

    from populus.contracts.utils import deploy_contract
    from populus.ethtester_client import EthTesterClient
    from populus.utils import get_contract_address_from_txn

    #: We enable populus plugin for this test file
    #: http://doc.pytest.org/en/latest/plugins.html#requiring-loading-plugins-in-a-test-module-or-conftest-file
    pytest_plugins = "populus.plugin",


    @pytest.fixture
    def ethtester_client() -> EthTesterClient:
        """Create ethtester client in sync mode.

        We use ethtester based testing where we run a faux blockchain directly in the process memory.
        This allows us to explicit control the creation of the new blocks, making testing
        a lot of easier.
        """
        client = EthTesterClient(async=False)
        return client


    @pytest.fixture
    def contract_address(ethtester_client: EthTesterClient) -> str:
        """Deploy a smart contract to local private blockchain so test functions can stress it out.

        :param ethtester_client: This is a py.test fixture for creating in-memory
            ethtester client

        :return: 0x prefixed hexadecimal address of the deployed contract
        """

        # This should be block 1 at the start of the test as
        # when we create ethtester_client is automatically
        # mines the first (genesis) block
        assert ethtester_client.get_block_number() == 1

        # We define the Populus Contract class outside the scope
        # of this example. It would come from compiled .sol
        # file loaded through Populus framework contract
        # mechanism.
        contract = get_wallet_contract_class()

        # Get a transaction hash where our contract is deployed
        deploy_txn_hash = deploy_contract(ethtester_client, contract)

        # Interacting with ethtester automatically mines a new block
        assert ethtester_client.get_block_number() == 2

        # Convert transaction hash from binary presentation
        # to hex string
        deploy_txn_hash = "0x" + binascii.hexlify(deploy_txn_hash).decode("utf-8")

        contract_addr = get_contract_address_from_txn(ethtester_client, deploy_txn_hash)

        return contract_addr

Using geth to run tests
-----------------------

`geth (go-ethereum) <https://github.com/ethereum/go-ethereum/>`__
is one of the most popular Ethereum node applications.
Populus provides facilities to spin up a geth service to run tests.
This geth will run a local test blockchain where you can quickly get response
for your transactions. The blockchain gets tore down at the
end of the test run.

In this local blockhain the mining difficulty is set to very
low to make sure you get blocks fast.

Stored blockchain files
+++++++++++++++++++++++

When run, ``chains/default-test`` folder is created in your
current working directory and that's where the block files
and account files are stored

Generating DAG dataset
++++++++++++++++++++++

geth performs real mining. `Mining requires dataset called
`DAG to be generated <https://github.com/ethereum/wiki/wiki/Ethash-DAG>`__.
The generation will take a lot of time, so you wish to recycle
chain files across test runs.

Each ethash set takes 1GB of space.

These files are shared across all geth instances. They are stored
in ``$HOME/.ethash` folder.

To generate initial DAG files you can do the following.

Create this faux py.test test case in your tests:

.. code-block:: python

    """Initialize local test geth node so that we can use it for mining.

    """
    import os
    import pytest

    from populus.geth import wait_for_geth_to_create_dag


    pytest_plugins = "populus.plugin",


    @pytest.mark.skipif(not os.environ.get("GETH_BOOTSTRAP"),
                        reason="Bootstrapping geth blockchain files is very slow operation and we want to run it only once.")
    def test_initialize_geth_node(geth_node_command: tuple, geth_coinbase):
        """Faux test case to create default-chain folder and initial mining files."""
        command, proc = geth_node_command

        # This will keep printing geth status updates until DAG files have
        # been created
        wait_for_geth_to_create_dag(proc)


Run the test to generate the DAG files:

.. code-block:: console

    GETH_BOOTSTRAP=1 py.test -s -k test_initialize_geth_node

Deploying a contract
++++++++++++++++++++

Below is an example py.test fixture to deploy a contract in Python 3 flavor:

.. code-block:: python

    import pytest

    from eth_rpc_client import Client

    from populus.contracts.utils import deploy_contract
    from populus.ethtester_client import EthTesterClient
    from populus.utils import get_contract_address_from_txn


    #: We enable populus plugin for this test file
    #: http://doc.pytest.org/en/latest/plugins.html#requiring-loading-plugins-in-a-test-module-or-conftest-file
    pytest_plugins = "populus.plugin",


    @pytest.fixture
    def contract_address(client: Client, geth_node, geth_coinbase: str) -> str:
        """Deploy a smart contract to local private blockchain so test functions can stress it out.

        :param client: py.test fixture to create RPC client to call geth node

        :param geth_node: py.test fixture to spin up geth node with test network parameters

        :param geth_coinbase: Ethereum account number for coinbase account where our mined ETHs appear

        :return: 0x prefixed hexadecimal address of the deployed contract
        """

        # Make sure that we have at least one block mined
        client.wait_for_block(1)

        # Make sure we have some ETH on coinbase account
        # so that we can deploy a contract
        assert client.get_balance(geth_coinbase) > 0

        # We define the Populus Contract class outside the scope
        # of this example. It would come from compiled .sol
        # file loaded through Populus framework contract
        # mechanism.
        contract = get_wallet_contract_class()

        # Get a transaction hash where our contract is deployed.
        # We set gas to very high randomish value, to make sure we don't
        # run out of gas when deploying the contract.
        deploy_txn_hash = deploy_contract(client, contract, gas=1500000)

        # Wait that the geth mines a block with the deployment
        # transaction
        client.wait_for_transaction(deploy_txn_hash)

        contract_addr = get_contract_address_from_txn(client, deploy_txn_hash)

        return contract_addr




