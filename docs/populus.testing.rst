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

    #: See :class:`populus.plugin.PopulusConfig` for configuration options
    deploy_client_type = 'rpc'


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