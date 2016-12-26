Testing
=======


Introduction
------------

The Populus framework provides some powerful utilities for testing your
contracts.  Testing in Populus is powered by the python testing framework
``py.test``.

All tests are run against an in-memory blockchain from ``pyethereum.tester``.

The convention for tests is to place them in the ``./tests/`` directory in the
root of your project.  In order for ``py.test`` to find your tests modules
their module name must start with ``test_``.

Running Tests With Pytest
~~~~~~~~~~~~~~~~~~~~~~~~~

To run the full test suite of your project:

.. code-block:: shell

    $ py.test tests/


Or to run a specific test

.. code-block:: shell

    $ py.test tests/test_greeter.py


Fixtures
--------

The test fixtures provided by populus are what make testing easy.  In order to
use a fixture in your tests all you have to do add an argument with the same
name to the signature of your test function.
 


Project
~~~~~~~

* ``project``

The :ref:`Project` object for your project.


.. code-block:: python

    def test_project_things(project):
        # directory things
        assert project.project_dir == '/path/to/my/project'

        # raw compiled contract access
        assert 'MyContract' in project.compiled_contracts


Unmigrated Chain
~~~~~~~~~~~~~~~~

* ``unmigrated_chain``

The ``'testrpc'`` test chain.  This chain will not have had migrations run.


.. code-block:: python

    def test_greeter(unmigrated_chain):
        greeter = unmigrated_chain.get_contract('Greeter')

        assert greeter.call().greet() == "Hello"

    def test_deploying_greeter(unmigrated_chain):
    
        GreeterFactory = unmigrated_chain.get_contract_factory('Greeter')
        
        # Manually deploy a contract
        deploy_txn_hash = GreeterFactory.deploy()

        # Wait for the transaction deploying the contract to be mined (~12s)
        deployed_address = chain.wait.for_contract_address(deploy_txn_hash)

        # Create a Contract proxy object to a deployed 
        # contract with a specific address. 
        # This proxy object contains Python call()
        # and transact() ABI wrappers.
        greeter = GreeterFactory(address=deployed_address)


Chain
~~~~~

* ``chain``

The same chain from the ``unmigrated_chain`` fixture except it has had all
migrations run ion it.


.. code-block:: python

    def test_greeter(chain):
        greeter = chain.get_contract('Greeter')

        assert greeter.call().greet() == "Hello"

    def test_deploying_greeter(chain):
        GreeterFactory = chain.get_contract_factory('Greeter')
        deploy_txn_hash = GreeterFactory.deploy()
        ...


Web3
~~~~

* ``web3``

A Web3.py instance configured to connect to ``chain`` fixture.

.. code-block:: python

    def test_account_balance(web3, chain):
        initial_balance = web3.eth.getBalance(web3.eth.coinbase)
        wallet = chain.get_contract('Wallet')

        withdraw_txn_hash = wallet.transact().withdraw(12345)
        after_balance = web3.eth.getBalance(web3.eth.coinbase)

        assert after_balance - initial_balance == 1234


Contracts
~~~~~~~~~

* ``contracts``

The contract factory classes for your project.  These will all be associated
with the Web3 instance from the ``web3`` fixture.

.. code-block:: python

    def test_wallet_deployment(web3, contracts):
        WalletFactory = contracts.Wallet

        deploy_txn_hash = WalletFactory.deploy()

.. note::

    For contracts that have library dependencies, you should use the
    ``Chain.get_contract_factory(...)`` api.  The contract factories from the
    ``contracts`` fixture will not be returned with linked bytecode.  The ones
    from ``Chain.get_contract_factory()`` are returned fully linked.


Accounts
~~~~~~~~

* ``accounts``

The ``web3.eth.accounts`` property off of the ``web3`` fixture


.. code-block:: python

    def test_accounts(web3, accounts):
        assert web3.eth.coinbase == accounts[0]


Custom Fixtures
---------------

The built in fixtures for accessing contracts are useful for simple contracts,
but this is often not sufficient for more complex contracts.  In these cases you can create you own fixtures to build on top of the ones provided by Populus.

One common case is a contract that needs to be given constructor arguments.
Lets make a fixture for a token contract that requires a constructor argument
to set the initial supply.

.. code-block:: python

    import pytest

    @pytest.fixture
    def token_contract(chain):
        TokenFactory = chain.get_contract_factory('Token')
        deploy_txn_hash = TokenFactory.deploy(arguments=[
            1e18,  # initial token supply
        )
        contract_address = chain.wait.for_contract_address(deploy_txn_hash)
        return TokenFactory(address=contract_address)


Now, you can use this fixture in your tests the same way you use the built-in
populus fixtures.

.. code-block:: python

    def test_initial_supply(token_contract):
        assert token_contract.call().totalSupply() == 1e18
