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
    TODO: actual command output


Once migrations have been initialized, you will be able to create your first
migration.  Lets write a migration to deploy the following Wallet contract.


.. code-block:: solidity

    // contracts/Wallet.sol

    contract Wallet {
        // TODO: a real contract body
    }


.. code-block:: shell

    $ populus makemigration deploy_wallet_contract
    TODO: actual command output

.. note::

    Currently, all migrations are generated empty (without any operations).
    You will need to add the desired operations to each migration you generate.

Now we will have a new python module located at
``./migrations/0001_deploy_wallet_contract.py``.


.. code-block:: python

    # -*- coding: utf-8 -*-
    from __future__ import unicode_literals

    from populus import migrations


    class Migration(migrations.Migration):

        migration_id = '0001_deploy_wallet_contract'
        dependencies = []
        operations = []
        compiled_contracts = {
            'Wallet': {
                # TODO: real bytecode
            }
        }


We can use the ``migrations.DeployContract`` operation to deploy our wallet
contract by adding it to the ``operations`` list for the migration.

.. code-block:: python

    # -*- coding: utf-8 -*-
    from __future__ import unicode_literals

    from populus import migrations


    class Migration(migrations.Migration):

        migration_id = '0001_deploy_wallet_contract'
        dependencies = []
        operations = [
            migrations.DeployContract(contract_name='Wallet'),
        ]
        compiled_contracts = {
            'Wallet': {
                # TODO: real bytecode
            }
        }


Now that we have a migration, lets run it on our local test chain that we
previously initialized.


.. code-block:: shell

    $ populus migrate
    # TODO: real command output.


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
