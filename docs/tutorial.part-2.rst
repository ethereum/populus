Part 2: Local Chains
====================

.. contents:: :local:


Introduction
------------

In part 1 of the tutorial we modified our ``Greeter`` contract and expanded the
test suite to cover the new functionality.

In this portion of the tutorial, we will explore the ability of populus to deploy the contracts
to the blockchain.

One of the nice things about Ethereum is the *protocol*, a protocol which specifies how to run a blockchain.
Theoretically, you can use this exact protocol to run your own blockchain, which is private and totally
seprated from the mainnet Ethereum blockchain and its nodes.

Although the private Ether you will mint in this private blockchain are not worth a lot in the outside world
(but who knows?), such private, local blockchain is a great tool for development. It simulates
the real ethereum blockchain, precisely, with the same protocol, but without the overhead of syncing,
running and waiting for the real testnet blockchain connections and data.

Once the contract is ready, working, and tested on your local chain, you can deploy it
to the distributed ethereum blockchains: testnet, the testing network, and then to the real Ethereum
blockchain, with real money and by paying real gas (in Eth) for the deployment.

In this tutorial we will create, and deploy to, a local chain we'll name "horton".

Create a *Local* chain
--------------------------

To create a new local chain in your project directory type:

.. code-block:: bash

      $ populus chain new horton

Check your project directory, which should look as follows:

.. code-block:: bash

  ├── chains
  │   └── horton
  │       ├── chain_data
  │       │   └── keystore
  │       │       └── UTC--2017-10-10T11-36-58.745314398Z--eb9ae85fa8f6d8853afe45799d966dca89edd9aa
  │       ├── genesis.json
  │       ├── init_chain.sh
  │       ├── password
  │       └── run_chain.sh
  ├── contracts
  │   └── Greeter.sol
  ├── project.json
  └── tests
      └── test_greeter.py

Let's unpack this.

First, we see the project's known structure: the project config file ``project.json``, and the ``contracts``
and ``tests`` directories.

The ``chain new`` command added a new directory: `chains`, and within it, the `horton` chain.

The ``chain_data`` directory is where geth will store the blockchain data. It's empty, for now,
since we didn't run this local chain at all.

.. _tutorial_wallets:

Wallets
'''''''

Then, the ``keystore`` directory, where the "wallets" are saved. A wallet file is a special file that
stores an ethereum account. Here we see one wallet file, ``UTC--2017-10-10T11-36-58.745314398Z--eb9ae85fa8f6d8853afe45799d966dca89edd9aa``.
The first part of the wallet file name is the time that the wallet was created,
and the second part is the account address. You should see similar file name on your machine,
but of course with a different time-stamp and a different address.

Here is the wallet:

.. code-block:: bash

  $ cat chains/horton/chain_data/keystore/UTC--2017-10-10T11-36-58.745314398Z--eb9ae85fa8f6d8853afe45799d966dca89edd9aa

  {
  "address":"eb9ae85fa8f6d8853afe45799d966dca89edd9aa",
  "crypto":{
    "cipher":"aes-128-ctr","ciphertext":"202bee426c48fd087e19a351d207f74903a437ea74cff5f7491ed0b82a591737",
    "cipherparams":{
      "iv":"02c18eab6f32875de56cb4452f7d4fa8"
      },
      "kdf":"scrypt",
      "kdfparams":{
        "dklen":32,"n":262144,"p":1,"r":8,"salt":"747653d095958f26666dd90a91b26bf00d0d848b37f9df26ad68badd004ee88f"
      },
      "mac":"ac8d6afd19a4dbd55b67ef94d31bb323f037346f6973b60b4948d5ab6ba7f6de"
    },
    "id":"9542872c-6855-4dcc-b45d-8654009a89c3",
    "version":3
 }

The wallet doesn't save any info regarding the account balance,
transactions, etc - this info is saved on the blockchain. It does, however, allows you to unlock an account, send Ethereum,
and run transactions with this account.

The wallet file is encrypted with a password. To unlock the account in the wallet, geth requires the password.
Here, populus saved the password in a password file:

.. code-block:: bash

  $ cat chains/horton/password
  this-is-not-a-secure-password

The default password we used, tells. It's designated for development and testing, not when using real Eth.

Why to save the password in a file *at all*? Because you can provide this file path
to geth with the ``password`` commnad line argument. Otherwise, you will have to manually enter
the password each time geth starts. Moreover, sometimes it's hard to spot the password prompt
with all the info that geth spits. So a password file is more convinient, but obviously should be fully secured,
with the right permissions.

.. _tutorial_accounts:

Accounts
''''''''

Populus created the account for you, but you can create more accounts with ``$ geth account new``. You can keep
as many wallets as you want in the keystore. One wallet, which you can set, is the primary default account, called
"etherbase" or "coinbase". You can use any wallet you save in the keystore, as long as you have the password to unlock it.
See `geth accounts managment <https://github.com/ethereum/go-ethereum/wiki/Managing-your-accounts>`_ .

.. note::

   The terms "create an account", or "new account", may be missleading. Nobody "creates" an account,
   since all the possible alphanumeric combinations of a valid Ethereum account address are already "out there".
   But any combination is useless, if you don't have the
   private key for this particular combination. "Create" an account means to start with a private key,
   and then **find** the combination, the address, which is derived from this specific private key
   (actually from the public key, which itself is derived from the private key).

The Genesis Block
'''''''''''''''''

The next file is ``genesis.json```. This is the definition of the first block of the chain,
which is called the "genesis" block. Every blockchain starts with an initial genesis block, the #0 block.
The real ethereum genesis block can be seen `here <https://etherscan.io/block/0>`_.

Take a look at the horton genesis block:

.. code-block:: bash

  $ cat chains/horton/genesis.json

  {
    "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
   "coinbase": "0xeb9ae85fa8f6d8853afe45799d966dca89edd9aa",
   "extraData": "0x686f727365",
   "config": {
       "daoForkBlock": 0,
       "daoForSupport": true,
       "homesteadBlock": 0
    },
   "timestamp": "0x0",
    "mixhash": "0x0000000000000000000000000000000000000000000000000000000000000000",
    "nonce": "0xdeadbeefdeadbeef",
    "alloc": {
        "0xeb9ae85fa8f6d8853afe45799d966dca89edd9aa":{
          "balance": "1000000000000000000000000000000"
      }
      },
    "gasLimit": "0x47d5cc",
    "difficulty": "0x01"
 }

The genesis block parent hash is 0, since it's the first block.

The nice thing about having your very own money minting facility,
is that you can mint money quite easily! So the genesis block allocates to the default account not less than one billion ether.
Think of it as monopoly money: it looks like real money, it behaves like real money, but it will not get you much in the grocery store.
However, this local chain Eth is very handy for development and testing.

.. _runing_local_blockchain:

Running the Local Blockchain
----------------------------

Great. Everything is in place to run your own local blockchain.

Before the first run, you need to initiate this blockchain.
Go ahead and init the chain, with the script that populus created:

.. code-block:: bash

  $ chains/horton/./init_chain.sh

Geth will init the blockchain:

.. code-block:: bash

  INFO [10-10|07:17:48] Allocated cache and file handles         database=/home/marry/projects/myproject/chains/horton/chain_data/geth/chaindata cache=16 handles=16
  INFO [10-10|07:17:48] Writing custom genesis block
  INFO [10-10|07:17:48] Successfully wrote genesis state         database=chaindata                                                                   hash=ab7daa…b26156
  INFO [10-10|07:17:48] Allocated cache and file handles         database=/home/marry/projects/myproject/chains/horton/chain_data/geth/lightchaindata cache=16 handles=16
  INFO [10-10|07:17:48] Writing custom genesis block
  INFO [10-10|07:17:48] Successfully wrote genesis state         database=lightchaindata                                                                   hash=ab7daa…b26156

.. note::

  You need to run the init script only once for each new chain


When geth created the blockchain, it added some files, where it stores the blockchain data:

.. code-block:: bash

  chains/
  └── horton
      ├── chain_data
      │   ├── geth
      │   │   ├── chaindata
      │   │   │   ├── 000001.log
      │   │   │   ├── CURRENT
      │   │   │   ├── LOCK
      │   │   │   ├── LOG
      │   │   │   └── MANIFEST-000000
      │   │   └── lightchaindata
      │   │       ├── 000001.log
      │   │       ├── CURRENT
      │   │       ├── LOCK
      │   │       ├── LOG
      │   │       └── MANIFEST-000000
      │   └── keystore
      │       └── UTC--2017-10-10T14-17-37.895269081Z--62c4b5955c028ab16bfc5cc57e09af6370a270a1
      ├── genesis.json
      ├── init_chain.sh
      ├── password
      └── run_chain.sh


Finally, you can run your own local blockchain!

.. code-block:: bash

  $ chains/horton/./run_chain.sh

And you should see geth starting to actually run the blockchain:

.. code-block:: bash

  INFO [10-10|07:20:45] Starting peer-to-peer node               instance=Geth/v1.6.7-stable-ab5646c5/linux-amd64/go1.8.1
  INFO [10-10|07:20:45] Allocated cache and file handles         database=/home/mary/projects/myproject/chains/horton/chain_data/geth/chaindata cache=128 handles=1024
  WARN [10-10|07:20:45] Upgrading chain database to use sequential keys
  INFO [10-10|07:20:45] Initialised chain configuration          config="{ChainID: <nil> Homestead: 0 DAO: 0 DAOSupport: false EIP150: <nil> EIP155: <nil> EIP158: <nil> Metropolis: <nil> Engine: unknown}"
  INFO [10-10|07:20:45] Disk storage enabled for ethash caches   dir=/home/mary/projects/myproject/chains/horton/chain_data/geth/ethash count=3
  INFO [10-10|07:20:45] Disk storage enabled for ethash DAGs     dir=/home/mary/.ethash                                                      count=2
  WARN [10-10|07:20:45] Upgrading db log bloom bins
  INFO [10-10|07:20:45] Bloom-bin upgrade completed              elapsed=163.975µs
  INFO [10-10|07:20:45] Initialising Ethereum protocol           versions="[63 62]" network=1234
  INFO [10-10|07:20:45] Loaded most recent local header          number=0 hash=ab7daa…b26156 td=1
  INFO [10-10|07:20:45] Loaded most recent local full block      number=0 hash=ab7daa…b26156 td=1
  INFO [10-10|07:20:45] Loaded most recent local fast block      number=0 hash=ab7daa…b26156 td=1
  INFO [10-10|07:20:45] Starting P2P networking
  INFO [10-10|07:20:45] HTTP endpoint opened: http://127.0.0.1:8545
  INFO [10-10|07:20:45] WebSocket endpoint opened: ws://127.0.0.1:8546
  INFO [10-10|07:20:45] Database conversion successful
  INFO [10-10|07:20:45] RLPx listener up                         self="enode://dc6e3733c416843a35b829c4edf5452674fccf4d0e9e25d026ae6fe82a06ff600958d870c505eb4dd877e477ffb3831a10661f928820cf1dad3d3c5d494516ff@[::]:30303?discport=0"
  INFO [10-10|07:20:45] IPC endpoint opened: /home/mary/projects/myproject/chains/horton/chain_data/geth.ipc
  INFO [10-10|07:20:46] Unlocked account                         address=0x62c4b5955c028ab16bfc5cc57e09af6370a270a1
  INFO [10-10|07:20:46] Transaction pool price threshold updated price=1800000000

Note the IPC (in process communication) endpoint line: ``IPC endpoint opened: /home/mary/projects/myproject/chains/horton/chain_data/geth.ipc``.
The actual path on your machine should match the project path.

IPC allows connection from the same machine, which is safer.


Where the Blockchain is Actually Running?
-----------------------------------------

The blockchain that runs now does not relate to populus. Populus just created some files, but the chain is
an independent geth process which runs on your machine.

You can verify it, using the web3 javascript console. In another terminal, open a console that attaches to this blockchain:

.. code-block:: bash

  $ geth attach /home/mary/projects/myproject/chains/horton/chain_data/geth.ipc

Use the actual IPC endpoint path that runs on your machine. You can take a look at ``run_chain.sh``
to see this path.

The web3.js console looks like this :

.. code-block:: bash

  Welcome to the Geth JavaScript console!

  instance: Geth/v1.6.7-stable-ab5646c5/linux-amd64/go1.8.1
  coinbase: 0x62c4b5955c028ab16bfc5cc57e09af6370a270a1
  at block: 9 (Tue, 10 Oct 2017 07:30:00 PDT)
   datadir: /home/may/projects/myproject/chains/horton/chain_data
   modules: admin:1.0 debug:1.0 eth:1.0 miner:1.0 net:1.0 personal:1.0 rpc:1.0 txpool:1.0 web3:1.0

  >

Check your account balance:

.. code-block:: bash

  > web3.fromWei(eth.getBalance(eth.coinbase))
  1000000000160
  >

Wow! you already have even more than the original allocation of one billion! These are the rewards for successful mining. Boy, the rich get richer.

.. note::

  Wei is the unit that `getBalance` returns by default, and `fromWei` converts Wei to Ethereum.
  See the `Ethereum units denominations <http://ethdocs.org/en/latest/ether.html#denominations>`_


You can work in the geth console and try other web3.js commands.
But as much as we love javascript, if you were missing those brackets and semicolons you would
not be here, in the Populus docs, would you?

So the next step is to deploy the Greeter contract with Populus to the horton local chain.

.. note::

  To stop geth, go the terminal where it's running, and type Ctrl+C. If it runs as a daemon,
  use ``kill INT <pid>``, where pid is the geth process id.
