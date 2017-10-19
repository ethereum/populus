Part 6: Contract Instance on a Local Chain
==========================================

.. contents:: :local:

Deploy to a Local Chain
-----------------------

So far we worked with the ``tester`` chain, which is ephimeral: it runs only on memory, reset in each test,
and nothing is saved after it's done.

The easiest *persisten* chain to start with, is a private local chain. It runs on your machine, saved to hard drive,
for persistency, and fast to respond. Yet it keeps the same Ethereum protocol, so everything that works locally
should work on ``testnet`` and ``mainnet``. See :ref:`runing_local_blockchain`

You already have ``horton``, a local chain, which you set when you started the project.

Run this chain:

.. code-block:: shell

    $ chains/horton/./run_chain.sh

And you will see that geth starts to do it's thing:

.. code-block:: shell

    INFO [10-18|19:11:30] Starting peer-to-peer node               instance=Geth/v1.6.7-stable-ab5646c5/linux-amd64/go1.8.1
    INFO [10-18|19:11:30] Allocated cache and file handles         database=/home/mary/projects/donations/chains/horton/chain_data/geth/chaindata cache=128 handles=1024
    INFO [10-18|19:11:30] Initialised chain configuration          config="{ChainID: <nil> Homestead: 0 DAO: 0 DAOSupport: false EIP150: <nil> EIP155: <nil> EIP158: <nil> Metropolis: <nil> Engine: unknown}"
    INFO [10-18|19:11:30] Disk storage enabled for ethash caches   dir=/home/mary/projects/donations/chains/horton/chain_data/geth/ethash count=3
    INFO [10-18|19:11:30] Disk storage enabled for ethash DAGs     dir=/home/mary/.ethash

The chain runs as an independent geth process, that is not related to Populus (Populus just created the setup files).
Let the chain run. Open another terminal, and deploy the contract to ``horton``:

.. code-block:: shell

    $ populus deploy --chain horton Donator --no-wait-for-sync

    > Found 1 contract source files
    - contracts/Donator.sol
    > Compiled 1 contracts
    - contracts/Donator.sol:Donator
    Beginning contract deployment.  Deploying 1 total contracts (1 Specified, 0 because of library dependencies).
    Donator

    Deploy Transaction Sent: 0xc2d2bf95b7de4f63eb5712d51b8d6ebe200823e0c0aed524e60a411dac379dbc
    Waiting for confirmation...

And after a few seconds the transaction is mined:

.. code-block:: shell

    Transaction Mined
    =================
    Tx Hash      : 0xc2d2bf95b7de4f63eb5712d51b8d6ebe200823e0c0aed524e60a411dac379dbc
    Address      : 0xb8d9d2afbe18fd6ac43042164ece9691eb9288ed
    Gas Provided : 301632
    Gas Used     : 201631


    Verified contract bytecode @ 0xb8d9d2afbe18fd6ac43042164ece9691eb9288ed
    Deployment Successful.

If you looked at the other terminal window, where the chain is running, you would also see
the contract creation transaction:

.. code-block:: shell

    INFO [10-18|19:28:58] Commit new mining work                   number=62 txs=0 uncles=0 elapsed=139.867µs
    INFO [10-18|19:29:02] Submitted contract creation              fullhash=0xc2d2bf95b7de4f63eb5712d51b8d6ebe200823e0c0aed524e60a411dac379dbc contract=0xb8d9d2afbe18fd6ac43042164ece9691eb9288ed
    INFO [10-18|19:29:03] Successfully sealed new block            number=62 hash=183d75…b0ce05
    INFO [10-18|19:29:03] 🔗 block reached canonical chain          number=57 hash=1f9cc1…b2ebe3
    INFO [10-18|19:29:03] 🔨 mined potential block                  number=62 hash=183d75…b0ce05

Note that when Populus created ``horton``, it also created a wallet file, a password,
and added the ``unlock`` and ``password`` arguments to the ``geth`` command in the
run script, ``run_chain.sh``.

The same account also gets an allocation of (dummy) Ether
in the first block of the ``horton`` local chain, and this is why we can use ``--no-wait-for-sync``.
Otherwise, if your account get money from a transaction in a far (far away) block, that
was not synced yet localy, geth thinks that you don't have the funds for gas, and refuses to
deploy until you sync.

.. note::
    When you work with ``mainnet`` and ``testnet`` you will need to create your own wallet, password, and get
    some Ether (dummy Ether in the case of testnet) for the gas. See :ref:`deploy_to_local_chain`


Persistence of the Contract Instance
------------------------------------

Unlike the previous runs of the tests on the ``tester`` chain, this time the contract instance is persistent on the
local ``horton`` blockchain.

Check for yourself. Add the following script to your project.

.. code-block:: shell

    $ mkdir scripts
    $ nano scripts/donator.py

The script should look as follows:



.. code-block:: python

    from populus.project import Project

    p = Project(project_dir="/home/mary/projects/donations/")
    with p.get_chain('horton') as chain:
        donator, deploy_tx_hash = chain.provider.get_or_deploy_contract('Donator')

    print("Donator address on horton is {address}".format(address=donator.address))
    if deploy_tx_hash is None:
        print("The contract is already deployed on the chain")
    else:
        print("Deploy Transaction {tx}".format(tx=deploy_tx_hash))

It starts by initiating a Populus ``Project``. The Project is the enrty point
to the Populus API, where you can get all the relevant resources programatically.

.. note::

    we used an *absolute* path,
    so this script can be saved and run from anywhere on your machine.

The next line gets the ``horton`` chain object:

.. code-block:: python

    with p.get_chain('horton') as chain

Using ``get_chain``, the Populus Project object has access to any chain that is defined in the project's configuration file,
``project.json``, and the user-scope configuration file, ``~/.popuplus/config.json``. Go ahead
and take a look at the ``chains`` key in those files. Populus' config files are in JSON: not so pretty to the Pythonic
developer habbits, but for blockchain development it safer to use non programmble, static, external files (and hey, you got
to admit that Populus saves you form quite a lot javascript).


The ``chain`` is wrapped in a *context manager*, because it needs
to run initialisation code when it starts, and cleanup when done. The code inside the ``with`` clause
runs after initialisation, and when it finishes, python runs the exit code for you.

The next line should be familiar to you by now:

.. code-block:: python

     donator, deploy_tx_hash = chain.provider.get_or_deploy_contract('Donator')


Populus does it's magic:

**New**: If the contract was *never* deployed to a blockchain, compile the source,
deploy to the chain, create a Web3 contract Python object instance, which points to the blockchain bytecode, and returns this Python object.

**Existing**: If the contract *was already deployed*, that is the contract's bytecode *already* sits
on the blockchain and has an address, populus just create the Python object instance for this bytecode.

Time to check it, just make sure that the ``horton`` chain runs (``chains/horton/./run_chain.sh``).

Run the script:

.. code-block:: shell

    $ python scripts/donator.py

    Donator address on horton is 0xb8d9d2afbe18fd6ac43042164ece9691eb9288ed
    The contract is already deployed on the chain

Ok, Populus found the contract on the chain, at exactly the same address.

.. note::

    You may need to run the script with ``$ python3``

To make sure it's persistent, stop the chain, then run it again.
Type Ctrl+C in the running chain window:

.. code-block:: shell

    INFO [10-19|05:28:09] WebSocket endpoint closed: ws://127.0.0.1:8546
    INFO [10-19|05:28:09] HTTP endpoint closed: http://127.0.0.1:8545
    INFO [10-19|05:28:09] IPC endpoint closed: /home/mary/projects/donations/chains/horton/chain_data/geth.ipc
    INFO [10-19|05:28:09] Blockchain manager stopped
    INFO [10-19|05:28:09] Stopping Ethereum protocol
    INFO [10-19|05:28:09] Ethereum protocol stopped
    INFO [10-19|05:28:09] Transaction pool stopped
    INFO [10-19|05:28:09] Database closed     database=/home/mary/projects/donations/chains/horton/chain_data/geth/chaindata


Geth stopped. Re-run it:

.. code-block:: shell

    $ chains/horton/./run_chain.sh

    INFO [10-19|05:34:23] Starting peer-to-peer node               instance=Geth/v1.6.7-stable-ab5646c5/linux-amd64/go1.8.1
    INFO [10-19|05:34:23] Allocated cache and file handles         database=/home/mary/projects/donations/chains/horton/chain_data/geth/chaindata cache=128 handles=1024
    INFO [10-19|05:34:23] Initialised chain configuration          config="{ChainID: <nil> Homestead: 0 DAO: 0 DAOSupport: false EIP150: <nil> EIP155: <nil> EIP158: <nil> Metropolis: <nil> Engine: unknown}"

Then, in another terminal window run the script again:

.. code-block:: shell

    $ python scripts/donator.py

    Donator address on horton is 0xb8d9d2afbe18fd6ac43042164ece9691eb9288ed
    The contract is already deployed on the chain

Same contract, *same* address. The contract is persistent on the blockchain. It is *not* re-deployed on each run,
like the ``tester`` in-memory ephemeral chain that we used in the tests, and was reset for each test.

.. note::

    Persistence for a local chain is simply it's data directory on your local hard-drive. It's a one-peer chain. On
    ``mainnet`` and ``testnet`` this persistency is synced between many nodes on the blockchain. However the concept is the same:
    a persistent contract.

Registrar
---------

When Populus deploys a contract to a blockchain, is saves the deployment details in ``registrar. json`` file.
This is how you project directory should look:

.. code-block:: shell

    ├── build
    │   └── contracts.json
    ├── chains
    │   └── horton
    │       ├── chain_data
    |       |     |
    |       |     └── ...
    │       └── nodekey
    │       │   └── keystore
    │       │       └── UTC--...
    │       ├── genesis.json
    │       ├── init_chain.sh
    │       ├── password
    │       └── run_chain.sh
    ├── contracts
    │   └── Donator.sol
    ├── project.json
    ├── registrar.json
    ├── scripts
    │   └── donator.py
    └── tests
        └── test_donator.py


The *registrar* is loaded with ``get_or_deploy_contract``, and if Populus finds an entry for a contract, it knows
that the contract already deployed, and it's address on this chain.

Take a look at the registrar:

.. code-block:: shell

    $ cat registrar.json

    {
  "deployments": {
    "blockchain://c77836f10cb9691c430638647b95701568ace603d0876ff41c6f0b61218254b4/block/667aa2e5f0dea4087b645a9287efa181cf6dad4ed96516b63aefb7ef5c4b1dff": {
      "Donator": "0xb8d9d2afbe18fd6ac43042164ece9691eb9288ed"
    }
  }



The registrar saves a deployment reference with unique "signature" of the blockchain that the contract was deployed to.
The signature is the first block hash, which is obviously unique. It appears after the ``blockchain://`` part. Then the hash
of the latest block at the time of deployment after, ``block``.
The registrar uses a special URI structure designed for blockchains, which is built from a resource name (blockchain, block, etc)
and it's hash. See `BIP122 URI <https://github.com/bitcoin/bips/blob/master/bip-0122.mediawiki>`_

To have *another* contract deployed to the *same* chain, we will greet our good ol' friend, the Greeter. Yes, you probably
missed it too.

.. code-block:: shell

    $ nano contracts/Greete.sol

Edit the contract file:

.. code-block:: solidity

    pragma solidity ^0.4.0;

    contract Greeter {
        string public greeting;

        function Greeter() {
            greeting = 'Hello';
        }

        function setGreeting(string _greeting) public {
            greeting = _greeting;
        }

        function greet() constant returns (string) {
            return greeting;
        }
    }


Deploy to ``horton``, after you make sure the chain runs:

.. code-block:: shell

    $ populus deploy --chain horton Greeter --no-wait-for-sync


You should see the usuall deployment log, and in a few seconds the contract creation transaction is picked and mined:

.. code-block:: shell

    Transaction Mined
    =================
    Tx Hash      : 0x5df249ed014b396655724bd572b4e44cbc173ab1b5ba5fdc61d541a39daa6d59
    Address      : 0xc5697df77a7f35dd1eb643fc2826c79d95b0bd76
    Gas Provided : 465580
    Gas Used     : 365579


    Verified contract bytecode @ 0xc5697df77a7f35dd1eb643fc2826c79d95b0bd76
    Deployment Successful.

Now we have two deployments to ``horton``:

.. code-block:: shell

    $ cat registrar.json

    {
  "deployments": {
    "blockchain://c77836f10cb9691c430638647b95701568ace603d0876ff41c6f0b61218254b4/block/34f52122cf90aa2ad90bbab34e7ff23bb8619d4abb2d8e66c52806ec9b992986": {
      "Greeter": "0xc5697df77a7f35dd1eb643fc2826c79d95b0bd76"
    },
    "blockchain://c77836f10cb9691c430638647b95701568ace603d0876ff41c6f0b61218254b4/block/667aa2e5f0dea4087b645a9287efa181cf6dad4ed96516b63aefb7ef5c4b1dff": {
      "Donator": "0xb8d9d2afbe18fd6ac43042164ece9691eb9288ed"
    }
  }


The blockchain id for the two deployments is the same, but the latest block at the time of deployment is obviously
different.

.. note::

    Don't edit the registrar yourself unless you know what you are doing. The edge case that justifies such
    edit is when you have a a project with contract that is already deployed on the ``mainnet``, and you want
    to include it in another project.  Re-deployment will waste gas. Otherwise, you can just re-deploy.


Contract Instances on More than One Chain
-----------------------------------------

We will create another instance of ``Donator``, but on another chain we'll name ``morty``.

Create and init the chain:

.. code-block:: shell

    $ populus chain new morty
    $ chains/morty/./init_chain.sh

Edit the project config file to include the new ``morty`` chain:

.. code-block:: shell

    $ nano project.json

The file should look as follows:

.. code-block:: javascript

    {
      "version":"7",
      "compilation":{
        "contracts_source_dirs": ["./contracts"],
        "import_remappings": []
      },
      "chains": {
        "horton": {
          "chain": {
            "class": "populus.chain.ExternalChain"
          },
          "web3": {
            "provider": {
              "class": "web3.providers.ipc.IPCProvider",
            "settings": {
              "ipc_path":"/home/mary/projects/donations/chains/horton/chain_data/geth.ipc"
            }
           }
          },
          "contracts": {
            "backends": {
              "JSONFile": {"$ref": "contracts.backends.JSONFile"},
              "ProjectContracts": {
                "$ref": "contracts.backends.ProjectContracts"
              }
            }
          }
        },
        "morty": {
          "chain": {
            "class": "populus.chain.ExternalChain"
          },
          "web3": {
            "provider": {
              "class": "web3.providers.ipc.IPCProvider",
            "settings": {
              "ipc_path":"/home/mary/projects/donations/chains/morty/chain_data/geth.ipc"
            }
           }
          },
          "contracts": {
            "backends": {
              "JSONFile": {"$ref": "contracts.backends.JSONFile"},
              "ProjectContracts": {
                "$ref": "contracts.backends.ProjectContracts"
              }
            }
          }
        }
      }
    }


Fix the ``ipc_path`` to the actual ipc_path on your machine, you can see it in the run file at ``chains/morty/run_chain.sh``.

Run the **horton** chain:

.. code-block:: shell

    $ chains/horton/./run_chain.sh

And try to deploy again ``Donator`` to ``horton``, although we know it's already deployed to this chain:

.. code-block:: shell

    $ populus deploy --chain horton Donator --no-wait-for-sync

     Found 2 contract source files
  - contracts/Donator.sol
  - contracts/Greeter.sol
  > Compiled 2 contracts
  - contracts/Donator.sol:Donator
  - contracts/Greeter.sol:Greeter
  Beginning contract deployment.  Deploying 1 total contracts (1 Specified, 0 because of library dependencies).

 Donator
 Found existing version of Donator in registrar. Would you like to use
 the previously deployed contract @ 0xb8d9d2afbe18fd6ac43042164ece9691eb9288ed? [True]:

Populus found a matching entry for ``Donator`` deployment on the ``horton`` chain, and suggest to use it.
For now, accept and prompt ``True``:

.. code-block:: shell

    Deployment Successful.

Success message, but without a new transaction and new deployment, just use the already deployed instance on ``horton``.

Good. Stop the ``horton`` chain with Ctrl+C, and start **morty**:

.. code-block:: shell

    $ chains/morty/./run_chain.sh

    INFO [10-19|09:41:28] Starting peer-to-peer node instance=Geth/v1.6.7-stable-ab5646c5/linux-amd64/go1.8.1

And deploy to ``morty``:

.. code-block:: shell

    $ populus deploy --chain morty Donator --no-wait-for-sync

This time a new contract is deployed to the ``morty`` chain:

.. code-block:: shell

  > Found 2 contract source files
  - contracts/Donator.sol
  - contracts/Greeter.sol
  > Compiled 2 contracts
  - contracts/Donator.sol:Donator
  - contracts/Greeter.sol:Greeter
  Beginning contract deployment.  Deploying 1 total contracts (1 Specified, 0 because of library dependencies).

    Donator
    Deploy Transaction Sent: 0x842272f0f2b1f026c6ef003769b1f6acc1b1e43eac0d053541f218e795615142
    Waiting for confirmation...

    Transaction Mined
    =================
    Tx Hash      : 0x842272f0f2b1f026c6ef003769b1f6acc1b1e43eac0d053541f218e795615142
    Address      : 0xcffb2715ead1e0278995cdd6d1736a60ff50c6a5
    Gas Provided : 301632
    Gas Used     : 201631


Registrar:

.. code-block:: shell

    $ cat registrar.json


Now with the new deployment:

.. code-block:: javascript

        {
      "deployments": {
        "blockchain://927b61e39ed1e14a6e8e8b3d166044737babbadda3fa704b8ca860376fe3e90b/block/2e9002f82cc4c834369039b87916be541feb4e2ff49036cafa95a23b45ecce73": {
          "Donator": "0xcffb2715ead1e0278995cdd6d1736a60ff50c6a5"
        },
        "blockchain://c77836f10cb9691c430638647b95701568ace603d0876ff41c6f0b61218254b4/block/34f52122cf90aa2ad90bbab34e7ff23bb8619d4abb2d8e66c52806ec9b992986": {
          "Greeter": "0xc5697df77a7f35dd1eb643fc2826c79d95b0bd76"
        },
        "blockchain://c77836f10cb9691c430638647b95701568ace603d0876ff41c6f0b61218254b4/block/667aa2e5f0dea4087b645a9287efa181cf6dad4ed96516b63aefb7ef5c4b1dff": {
          "Donator": "0xb8d9d2afbe18fd6ac43042164ece9691eb9288ed"
        }
      }
    }

To summarise, the project has two Solidity source files with two contracts. Both are deployed to the ``horton`` chain,
``blockchain://c77836f1...``. The ``Donator`` contract has *another* contract instance on the ``morty`` chain,
``blockchain://927b61e3...``. So the project has 3 contract instances on 2 chains.

.. note::

    It is very common to have more than on contract instance per source file. You can have one on a local chain,
    on ``testnet``, and production on ``mainent``


Interim Summary
---------------

* You deployed a persistent contract instance to a local chain
* You interacted with the ``Project`` object, which is the entry point to the Populus API
* You deployed the same Solidity source file on two seprated local chains, ``horton`` and ``morty``
* Deployments are saved in the the ``registrar``