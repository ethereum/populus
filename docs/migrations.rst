Migrations
==========

.. contents:: :local:

Introduction
------------

Migrations are like deployments except they are designed to handle anything
from the simplest deployment situations to extremely complex sets of contracts
with complex deployment logic and requirements.


Quick Start
^^^^^^^^^^^

In order to use the migrations feature, a chain must be *initialized*.  This
currently means deploying the built in Registrar contract as well as optionally
selecting a default account that deployment transactions should originate from.

.. code-block:: shell

    $ populus migrate init
    Accounts
    -----------------
    0 - 0x03c932f52524ea0a47b83e86feacd9f26465f0e1

    Enter the account address or the number of the desired account [0x03c932f52524ea0a47b83e86feacd9f26465f0e1]:
    Would you like set the address '0x03c932f52524ea0a47b83e86feacd9f26465f0e1' as the default`deploy_from` address for the 'local_a' chain? [y/N]: y
    Wrote updated chain configuration to '/Users/piper/sites/populus/populus.ini'
    Deploying Registrar
    Deploy Transaction Sent: 0xa92099e923d67aa6a277a97ad9b7d0a13c80f0bad337ad231168161d884d41e0
    Waiting for confirmation...

    Transaction Mined
    =================
    Tx Hash      : 0xa92099e923d67aa6a277a97ad9b7d0a13c80f0bad337ad231168161d884d41e0
    Address      : 0x58b5b1c2b0eb24d909d66a8057a6777c076e0c12
    Gas Provided : 1305591
    Gas Used     : 1205591


    Verifying deployed bytecode...
    Verified contract bytecode @ 0x58b5b1c2b0eb24d909d66a8057a6777c076e0c12 matches expected runtime bytecode
    Wrote updated chain configuration to '/Users/piper/sites/populus/populus.ini'

    The 'local_a' blockchain is ready for migrations.


Once a chain has been initialized for migrations, you will be able to create
your first migration.  Lets write a migration to deploy the following Wallet
contract.


.. code-block:: solidity

    // contracts/Wallet.sol
    contract Wallet {
        mapping (address => uint) public balanceOf;

        function deposit() {
            balanceOf[msg.sender] += 1;
        }

        function withdraw(uint value) {
            if (balanceOf[msg.sender] < value) throw;
            balanceOf[msg.sender] -= value;
            if (!msg.sender.call.value(value)()) throw;
        }
    }


.. code-block:: shell

    $ populus makemigration deploy_wallet_contract
    Wrote new migration to: migrations/0001_deploy_wallet_contract.py

.. note::

    Currently, all migrations are generated empty (without any operations).
    You will need to add the desired operations to each migration you generate.

Now we will have a new python module located at
``./migrations/0001_deploy_wallet_contract.py``.  All migrations are generated
empty and require you to add operations in order for it to do anything.  In
this case we can use the ``migrations.DeployContract`` operation to deploy our
wallet contract by adding it to the ``operations`` list for the migration.


.. code-block:: python

    # -*- coding: utf-8 -*-
    from __future__ import unicode_literals

    from populus import migrations


    class Migration(migrations.Migration):

        migration_id = '0001_deploy_wallet_contract'
        dependencies = []
        operations = [
            migrations.DeployContract('Wallet'),  # You need to add this line.
        ]
        compiled_contracts = {
            'Wallet': {
                # contents removed for brevity.
            },
        }


Now that we have a migration, lets run it on our local test chain that we
previously initialized.


.. code-block:: shell

    $ populus migrate local_a
    Migration operations to perform:
      0001_deploy_wallet_contract (1 operations):
        0 - <populus.migrations.operations.DeployContract object at 0x10e745080>
    Executing migrations:
      0001_deploy_wallet_contract... DONE


Now suppose that we want to deposit some money in this contract.  We can do so
with the ``populus.migrations.operations.TransactContract`` operation.  First
we need to generate a new migration.

.. code-block:: shell

    $ populus makemigration make_initial_deposit
    Wrote new migration to: migrations/0002_make_initial_deposit.py


Then we need to specify the details of the transaction that should be sent.

.. code-block:: python

	# -*- coding: utf-8 -*-
	from __future__ import unicode_literals

	from populus import migrations


	class Migration(migrations.Migration):

		migration_id = '0002_make_initial_deposit'
		dependencies = [
			'0001_deploy_wallet_contract',
		]
		operations = [
			migrations.TransactContract(
				contract_name='Wallet',
				method_name='deposit', 
				transaction={'value': 5000000000000000000},  # 5 ether
				contract_address=migrations.Address.defer(key="contract/Wallet"),
			)
		]

In order to be able to reference values that you may not be able to know ahead
of time, populus uses a special class for deferring the resolution of those
values.  In the migration shown above, the address of the ``Wallet`` contract
will be looked up from the registrar under the key ``contract/Wallet``.

Now we can run this migration which will result in 5 ether being deposited in
our wallet contract.

.. code-block:: shell

    $ populus migrate local_a

    Migration operations to perform:
      0002_make_initial_deposit (1 operations):
        0 - <populus.migrations.operations.TransactContract object at 0x104ab76d8>
    Executing migrations:
      0002_make_initial_deposit... DONE


Migrations
----------

Migrations are intended to facilitate both the deployment of simple contracts
as well as complex constellations of contracts that may require both complex
deployment logic as well as complex interactions with those contracts after
they have been deployed.

Each migration consists of the following four pieces of information.

** ``migration_id``

    This is an identifier which will be used by other migrations to handle dependencies.

** ``dependencies``

    A list of the ``migration_id`` values for other migrations that this
    migration depends on.  When migrations are generated, the latest migration
    is set as a dependency automatically.

    Complex migratino dependency graphs are allowed as long as the result is a
    `Directed Acyclic Graph`_.

** ``operations``

    A list of ``populus.migrations.operations.Operation`` objects.  These must
    be added by the user.

** ``compiled_contracts``

    A python dictionary containing the compiled contract assets.  These are
    present to freeze the state of the project contracts at the time the
    migration was generated.



Operations
----------

Operations are units of work that are executed during a migration.  Populus
provides the following operation classes.


* ``populus.migrations.operations.SendTransaction(transaction[, timeout=180])``

  Sends a transaction specified by ``transaction`` parameter.
  
  The ``transaction`` parameter should to be a dictionary containing some set
  of the standard transaction parameters accepted by
  ``web3.eth.sendTransaction``.

  The operation will wait up to the ``timeout`` value for the transaction to be
  mined unless set to ``None`` in which case the operation will continue on
  without waiting.


* ``populus.migrations.operations.DeployContract(contract_name[, transaction=None, arguments=None, verify=True, libraries=None, timeout=180)``

  Deployes the contract designated by ``contract_name`` from the migration's
  ``compiled_contracts`` property.

  If specified, the ``transaction`` parameter should to be a dictionary
  containing some set of the standard transaction parameters accepted by
  ``web3.eth.sendTransaction``.  This ``transaction`` may not designate a
  ``to`` value or a ``data`` value as they will be constructed via the contract
  method call.

  If specified, the ``arguments`` parameter should be a list of arguments which
  will be passed in as constructor arguments for the contract.

  When the ``verify`` argument is set to a truthy value (which it is by
  default) then the contract's bytecode will be verified once the deployment
  transaction has been mined.  This is done by checking equality between the
  expected bytecode, and the bytecode returned the contract's address with
  ``web3.eth.getCode``.

  If specified, the ``libraries`` parameter should be a dictionary which
  specified any library linking dependencies for this contract.  The keys
  should be the full names of the the library contracts and the values should
  be the library addresses.

  The operation will wait up to the ``timeout`` value for the deployment
  transaction to be mined unless set to ``None`` in which case the
  operation will continue on without waiting.


* ``populus.migrations.operations.TransactContract(contract_address, contract_name, method_name[, arguments=None, transaction=None, timeout=180)``

  Sends a transaction, calling the method named by the ``method_name`` argument
  on the contract designated by the ``contract_name`` parameter from the
  migration's ``compiled_contracts`` property at the address indicated by the
  ``contract_address`` parameter..

  The ``transaction`` parameter behaves the same way as with the
  ``DeployContract`` operation.

  The ``arguments`` parameter behaves the same way as with the
  ``DeployContract`` operation.

  The ``timeout`` parameter behaves the same way as with the
  ``DeployContract`` operation.


* ``populus.migrations.operations.RunPython(callback)``

  Executes the provided ``callback`` within the context of the migration.  The
  ``callback`` should be a function that can be called with the following
  function signature.

  ``callback(chain, compiled_contracts, **kwargs)``

  .. note:: The ``kwargs`` portion is to maintain compatibility with future changes to the migrations API.


Deferred Values
---------------

A deferred value is a value that will not be resolved until the execution of
the given operation.  All operation constructor arguments support using a
deffered value in place of the actual value, in which case it will be resolved
at execution time of the operation.

Populus provides the following deferred value classes that can be used in
conjunction with the Registrar contract to look values up from the registrar.

** ``populus.migrations.deferred.Address``
** ``populus.migrations.deferred.Bytes32``
** ``populus.migrations.deferred.UInt``
** ``populus.migrations.deferred.Int``
** ``populus.migrations.deferred.String``
** ``populus.migrations.deferred.Bool``

To use one of these classes as a migration argument, you should call the class
method ``.defer(key='some-registrar-key')``.  One of the more common use cases
for this is accessing the address of a migration that was deployed in a
previous migration.  In this case, we can get the latest deployed address of a
given contract under the key ``'contract/TheContractName'``.

.. code-block:: python

    class Migration(migrations.Migration):
        ...
        operations = [
            migrations.TransactContract(
                contract_name='TheContractName',
                contract_address=migrations.Address.defer(key='contract/TheContractName'),
                method_name='destroy',
            ),
        ]
        ...


.. _Directed Acycplic Graph: http://example.com/
