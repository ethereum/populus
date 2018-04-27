Introduction
============

.. contents:: :local:

Background
----------

The purpose of this tutorial is to go one step beyond the common "Hello World" Greeter example,
to the entire development cycle of an Ethereum smart contract, using Python. We will try to unpack
the confusing issues, clear up the mystery, and even have some fun when you dive into blockchain and contracts development.

The tools we will use are Populus and Web3.py

.. note::

    Web3 in general is the client side API that let you interacts with the blockchain. Populus is a
    development framework, that is built on top of Web3. If you are into javascript, you can use the
    `Truffle javascript framework <http://truffleframework.com/>`_, and Web3.js which ships with the
    ``geth`` client. If you prefer Python, then Populus and Web3.py are your friends.


We assume that your read 1-2 intros about Ethereum and the blockchain, and know Python.

You don't need the complex math of the elliptic curves, but to get a grasp of the basic concepts, and the basic idea: A system that prevents bad behaviour not by moral rules, but
by incentives. Incentive that make honest behaviour *more* profitable (let this bold concept sink in for a moment).

Development Steps
-----------------
We will take a walk through an entire contract development cycle, with Python, Populus and Web3.py.

Typical iteration will include:

* Writing the contract
* Testing, fixing bugs
* Deployment to a local chain, make sure everything works
* Deployment to testnet,
* Finally deployment to mainnet which will cost real gas
* Interaction with the contract on the blockchain.


Glossary
--------

Just a succinct reference, as a reminder if you need it during the tutorial (in a "chronological" order)

**Private Key**: A long combination of alphanumeric characters. There is almost zero chance that the algorithm
that creates this combination will create the same combination twice.

**Public Key**: A combination of alphanumeric characters that is derived from the private key. It's easy to derive
the public key from the private key, but the opposite is impossible.

**Address**: A combination of alphanumeric characters that is derived from the public key.

**Ethereum Account**: An address that is used on the blockchain. There are infinite potential combinations
of alphanumeric characters, but only when someone has the private key that the address was derived from,
this address can be used as an *account*.

**Transaction**: A message that one account sends to another. The message can contain Ether (the digital currency),
and data. The data is used to run a contract if the account has one.


**Pending Transaction**: A transaction that was sent to the network, but still waiting for a miner to include it
in a block, and to the network to accept this block.

**Why the private key and the public key?** The keys mechanism can confirm that the transaction was indeed authorised by the account owner,
that claims to sent it.

**Block**: A group of transactions

**Mining**: Bundling a group of transactions into a block

**Why mining is hard?** Because the miner needs to bundle the transactions with an additional input that requires significant
computational effort to find. Without this additional input, the block is not valid.

**Rewards**: The Ether reward that a miner gets when it finds a valid block

**Blockchain**: Well, it's a chain of blocks. Each block has a parent, and each time a new block
is found it is added to the blockchain on top of the current last block. When a block is added to the blockchain,
all the transactions in this blocks are accepted and carried out by all the nodes.

**Node**: A running instance of the blockchain. The nodes sync to one another. When there are conflicts,
e.g. if two nodes suggest two different block for the next block, the nodes gets a decision by consensus.

**Consensus**: Miners get rewards when they find a valid block, and a valid block is valid only if it's built on a valid parent block,
and *accepted by the majority of nodes on the blockchain*. So miners are incentivised to reject false blocks and false transactions.
They know that if they work on a false transaction (say a cheat), then there
is high probability that other nodes will reject it, and their work effort will be lost without rewards.
They prefer to find valid blocks with valid transactions, and send them as fast as possible to the blockchain.

**Uncles**: Miners get rewards when they find valid blocks, even if those blocks are *not* part
of the direct line of the blockchain.
If the blockchain is ``block1`` >> ``block2`` >> ``block3`` >> ``block4``, and a miner found another valid block on top of ``block3``, say ``block4a``,
but wasn't fast enough to introduce it to the chain, it will still get *partial* rewards.
The faster miner, of ``block4``, will get the *full* rewards. ``block4`` is included in the direct sequence of the blockchain,
and ``block4a``  is not used in the sequence but included as an "*uncle*".
The idea is to spread compensations among miners and avoid "the winner takes it all" monopoly.

**Contract**: The word ""contract" is used for three different (albeit related) concepts:
(1) A compiled runnable bytecode that sits on the blockchain (2) A Solidity source code contract definition
(3) A Web3 contract object

**EVM**: The Ethereum Virtual Machine, the (quite complex) piece of code that runs the Ethereum protocol. It accepts an Assembler like instructions,
and can run contracts after compilation to  this Assembler bytecode.

**Solidity**: A programming language, similar to javascript, designed for contract authors.

**Solc**: Compiler of Solidity source code to the EVM bytecode

**ABI**: Application Binary Interface. A JSON file that describes a contract interface: the functions that the
contract exposes, and their arguments. Since the contracts on the blockchain are a compiled bytecode,
the EVM needs the ABI in order to know how to call the bytecode.

**Web3**: Client side API that lets you interact with the blockchain. Web3.js is the javascript version, Web3.py is the Python one.

**geth**: The official implementation of an Ethereum blockchain node, written in Go

**gas**: The price that users pay to run computational actions on the blockchain (deploying a new contract, send money, run a contract function, storage, memory)

**mainnet**: The Ethereum blockchain

**testnet**: An Ethereum blockchain for testing. It behaves exactly as mainnet, but you don't use real Ether to send money and pay for the gas

**Local chain**: A blockchain that runs locally, has it's own blocks, and does not sync to any other blockchain. Useful for development
and testing

