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

A migration


Operations
----------

Each migratino is 


* ``populus.migrations.

TODO: operations stuff


Deferred Values
---------------

TODO: deferred value stuff.
