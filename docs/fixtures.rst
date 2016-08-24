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

.. note:: 

    The functionality and behavior of this fixture is likely to change
    significantly over the next few releases as it gets integrated with the
    migrations feature.

The deployed contract instances for all of your project contracts.


Accounts
--------

* ``accounts``

The ``web3.eth.accounts`` property off of the ``web3`` fixture
