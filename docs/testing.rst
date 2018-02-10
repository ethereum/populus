.. _populus_testing:

Testing
=======


Introduction
------------

The Populus framework provides some powerful utilities for testing your
contracts.  Testing in Populus is powered by the python testing framework
``py.test``.

By default tests are run against an in-memory ethereum blockchain.

The convention for tests is to place them in the ``./tests/`` directory in the
root of your project.  In order for ``py.test`` to find your tests modules
their module name must start with ``test_``.


Test Contracts
--------------

Populus supports writing contracts that are specifically for testing.  These
contract filenames should match the glob pattern ``Test*.sol`` and be located
anywhere under your project tests directory ``./tests/``.


Running Tests With Pytest
~~~~~~~~~~~~~~~~~~~~~~~~~

To run the full test suite of your project:

.. code-block:: shell

    $ py.test tests/


Or to run a specific test

.. code-block:: shell

    $ py.test tests/test_greeter.py


Pytest Fixtures
---------------

The test fixtures provided by populus are what make testing easy.  In order to
use a fixture in your tests all you have to do add an argument with the same
name to the signature of your test function.



Project
~~~~~~~

* ``project``

The Project object for your project.

This project object is initialised first, and the rest of the fixtures are derived from it.

.. code-block:: python

    def test_project_things(project):
        # directory things
        assert project.project_dir == '/path/to/my/project'

        # raw compiled contract access
        assert 'MyContract' in project.compiled_contract_data


How populus finds the project of the project fixture
''''''''''''''''''''''''''''''''''''''''''''''''''''

If no other argument is provided, populus defaults to using the current tests directory.
This is true if you run py.test from within the project's directory, or with a positional argument to this project's directory,
e.g. ``$ py.test /path/to/my/project/``.

If the tests are in a different directory, e.g. ``$ py.tests /path/to/tests/``,
you will have to provide the tested project:

1. With command line argument: ``$ py.test /path/to/tests/ --populus-project /path/to/my/project/``
2. Or, in a pytest.ini file, with the following entry: ``populus_project=/path/to/my/project/``
3. Or with an environment variable: ``PYTEST_POPULUS_PROJECT``. E.g., ``PYTEST_POPULUS_PROJECT=/path/to/my/project/ py.test /path/to/tests/``


The precedence order for these different methods of setting the project directory is:

#. command line
#. pytest.ini
#. environment variable


.. note:

    Providing only the propulus project arg (via command line, or pytest.ini, or the environment variable) will not replace
    py.test own tests finding. So you still need to provide pytest the correct tests directory, or rely on pytest tests
    collecting.

    So if you have a project at /home/username/projects/project_foo, then ``$ pytest --populus-project /home/username/projects/project_foo``
    may not work if you run it say from /home/elsewhere. The argument will only tell pytest where to load the project fixture, but
    not where the actual tests are.

    The nice thing is that you can run the same tests suite on diffrent projects, each time apply the same test to another project,
    where pytest will load the project fixture from another project.



Chain
~~~~~

* ``chain``

A running ``'tester'`` test chain.


.. code-block:: python

    def test_greeter(chain):
        greeter, _ = chain.provider.get_or_deploy_contract('Greeter')

        assert greeter.call().greet() == "Hello"

    def test_deploying_greeter(chain):
        GreeterFactory = chain.provider.get_contract_factory('Greeter')
        deploy_txn_hash = GreeterFactory.deploy()
        ...


Registrar
~~~~~~~~~

* ``registrar``

Convenience fixture for the ``chain.registrar`` property.


Provider
~~~~~~~~

* ``provider``

Convenience fixture for the ``chain.provider`` property.


Web3
~~~~

* ``web3``

A Web3.py instance configured to connect to ``chain`` fixture.

.. code-block:: python

    def test_account_balance(web3, chain):
        initial_balance = web3.eth.getBalance(web3.eth.coinbase)
        wallet = chain.get_contract('Wallet')

        withdraw_txn_hash = wallet.transact().withdraw(12345)
        withdraw_txn_receipt = chain.wait.for_receipt(withdraw_txn_hash)
        after_balance = web3.eth.getBalance(web3.eth.coinbase)

        assert after_balance - initial_balance == 1234

Base Contract Factories
~~~~~~~~~~~~~~~~~~~~~~~

* ``base_contract_factories``

The contract factory classes for your project.  These will all be
associated with the Web3 instance from the ``web3`` fixture.

.. code-block:: python

    def test_wallet_deployment(web3, base_contract_factories):
        WalletFactory = base_contract_factories.Wallet

        deploy_txn_hash = WalletFactory.deploy()

.. note::

    For contracts that have library dependencies, you should use the
    ``Chain.get_contract_factory(...)`` api.  The contract factories from the
    ``base_contract_factories`` fixture will not be returned with linked
    bytecode.  The ones from ``Chain.get_contract_factory()`` are returned
    fully linked.


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

    @pytest.fixture()
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
