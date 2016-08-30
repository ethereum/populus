Test fixtures
=============

The following `pytest <http://pytest.org>`__ fixtures are available for your tests.


.. code-block:: python

    def test_something(project):
        # directory things
        assert project.project_dir == '/path/to/my/project'

        # raw compiled contract access
        assert 'MyContract' in project.compiled_contracts

        # running any of the project chains.
        with project.get_chain('testrpc') as chain:
            web3 = chain.web3
            ...  # do something with the chain..


Project
-------

* ``project``

The ``populus.project.Project`` object for your project.


Chain
-----

* ``chain``

The ``'testrpc'`` test chain.


Web3
----

* ``web3``

The ``web3`` object off of the ``chain`` fixture.


Contracts
---------

* ``contracts``

The contract factory classes for your project.  These will all be associated
with the Web3 instance from the ``web3`` fixture.


Deployed Contracts
------------------

* ``deployed_contracts``

The deployed contract instances for all of your project contracts.  This data
is pulled from the data available fromt he registrar contract for the given
chain.  Only contracts which satisfy all of the following conditions will be
available in this fixture.

* Address found in the registrar contract
* All library dependencies are available in the registrar contract.
* All bytecode for both libraries and the given contract matches that of the
  latest compiled assets.


Accounts
--------

* ``accounts``

The ``web3.eth.accounts`` property off of the ``web3`` fixture
