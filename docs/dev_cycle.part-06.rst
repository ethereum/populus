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
run script, ``run_chain.sh``. The same account also gets an allocation of (dummy) Ether
in the first block of the ``horton`` local chain, and this is why we can use ``--no-wait-for-sync``.
Otherwise, if the transaction that sends money to your account is in a block that was not
synced yet to your local node, geth thinks you don't have money for the gas and refuses to
deploy.

When you work with ``mainnet`` and ``testnet`` you will need to create your own wallet, password, and get
some Ether for the gas. See :ref:`deploy_to_local_chain`








Interim Summary
---------------

    * Working Contract
    * All tests pass

The next step is to deploy the contract to a persisetent chain.




