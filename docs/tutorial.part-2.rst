Part 2: Local Chains
====================

.. contents:: :local:


Introduction
------------

In part 1 of the tutorial we modified our ``Greeter`` contract and expanded the
test suite to cover the new functionality.

In this portion of the tutorial we will explore the ability for populus to both
run nodes for you as well as connect to running nodes.


Setting up a *local* chain
--------------------------

The first thing we will do is setup a local chain.  Create a file in the root
of your project named ``populus.json`` with the following contents


.. code-block:: javascript

    {
      "chains": {
        "horton": {
          "web3": {
            "provider": {
              "class": "web3.providers.ipc.IPCProvider"
            }
          }
        }
      }
    }


We have just setup the minimal configuration necessary to run a local chain
named ``horton``.  You can run this chain now in yoru terminal with the
following command.


.. code-block:: bash

    $ populus chain run horton


You should see **alot** of very verbose output from the running geth node.  If
you wait and watch you will also see blocks being mined.


Deploying the contract
----------------------

Now that we have a local chain we can deploy our ``Greeter`` contract using the
``populus deploy`` command.  When prompted select the listed account.


.. code-block:: bash

    $ populus deploy --chain horton Greeter
    Beginning contract deployment.  Deploying 1 total contracts (1 Specified, 0 because of library dependencies).

    Greeter
    Accounts
    -----------------
    0 - 0xf142ff9061582b7b5f2f39f1be6445947a1f3feb

    Enter the account address or the number of the desired account [0xf142ff9061582b7b5f2f39f1be6445947a1f3feb]: 0
    Deploying Greeter
    Deploy Transaction Sent: 0xd3e6ad1ee455b37bd18703a6686575e9471101fbed7aa21808afd0495e026fe6
    Waiting for confirmation...

    TODO: remaining output


.. note:: Your output will differ in that the ethereum address and transaction hashes won't be the same.

It's worth pointing out some *special* properties of local chains.

* They run with all APIs enabled (RPC, IPC, WebSocket)
* They run with the coinbase unlocked.
* They mine blocks using a single CPU.
* Their ``datadir`` is located in the ``./chains`` directory within your project.
* The coinbase account is alotted a **lot** of ether.

Having to select which account to deploy from each time you deploy on a chain
is tedious.  Lets modify our configuration to specify what the *default* deploy
address should be.  Change your configuration to match this.

.. code-block:: javascript

    {
      "chains": {
        "horton": {
          "web3": {
            "provider": {
              "class": "web3.providers.ipc.IPCProvider"
            },
            "eth": {
              "default_account": "0xf142ff9061582b7b5f2f39f1be6445947a1f3feb"
            }
          }
        }
      }
    }

You can test this now by deploying the greeter contract again using the same
command from above.  If everything is configured correctly you should no longer
be prompted to select an account.
