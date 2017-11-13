Part 1: Solidity Contract
=====================

.. contents:: :local:


Start a New Project
-------------------

Create a directory for the project:

.. code-block:: bash

    $ mkdir projects projects/donations
    $ cd projects/donations
    $ populus init

    Wrote default populus configuration to `./project.json`.
    Created Directory: ./contracts
    Created Example Contract: ./contracts/Greeter.sol
    Created Directory: ./tests
    Created Example Tests: ./tests/test_greeter.py


You just created a new populus project. Populus created an example contract called ``Greeter`` and some tests.
To learn about the greeter example see the :ref:`Quickstart <greete_quickstart>`.

We will need a local private blockchain. This local blockchain
is an excellent tool for development: it runs on your machine, does not take the time to sync the real blockchain, does not
costs real gas and fast to respond.
Yet the local chain works with the same Ethereum protocol. If a contract runs
on the local chain, it should run on mainnet as well.

.. note::
    If you are familiar to web development, then running a local blockchain is
    similar to running a local website on 127.0.0.1, before publishing it to the internet.

We will create a a local chain we'll name "horton":

.. code-block:: bash

    $ populus chain new horton
    $ chains/horton/./init_chain.sh

    INFO [10-14|12:31:31] Allocated cache and file handles         database=/home/mary/projects/donations/chains/horton/chain_data/geth/chaindata cache=16 handles=16
    INFO [10-14|12:31:31] Writing custom genesis block
    INFO [10-14|12:31:31] Successfully wrote genesis state         database=chaindata                                                                        hash=faa498…370bf1
    INFO [10-14|12:31:31] Allocated cache and file handles         database=/home/mary/projects/donations/chains/horton/chain_data/geth/lightchaindata cache=16 handles=16
    INFO [10-14|12:31:31] Writing custom genesis block
    INFO [10-14|12:31:31] Successfully wrote genesis state         database=lightchaindata                                                                        hash=faa498…370bf1

Add this local chain to the project config.

.. code-block:: shell

    $ nano project.json

The file should look as follows. Update ``ipc_path`` to the actual path on
your machine (if you are not sure about the path, take a
look at ``chains/horton/run_chain.sh``).

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
      }
    }
  }


For more on the horton local chain see :ref:`runing_local_blockchain` .

Everything is ready.

Add a Contract
----------------

Ok, time to add a new contract.

.. code-block:: shell

    $ nano contracts/Donator.sol


.. note::

    You can work with your favourite IDE. Check for Solidity extention/package. Atom.io
    has some nice Solidity packages.


In this example we will work with a very simple contract that accepts donations for later use.
The contract will also handle the donations value in USD.

Since the ETH/USD exchange rate fluctates, typically upward, we want to track not only how much ETH the contract collected,
but also the accumulating USD value of the donations *at the time of the donation*.
If the ETH rate is rising, then we will probably see smaller donations
in terms of Ether, but similar donations in terms of USD.

In other words, two donations of say $30 will have different amounts in ETH if the exchange rate changed between
the donations. As a simple solution, we will ask donators to provide the effective ETH/USD exchange rate when they send their (hopefully generous) donations.


Here is the new contract code:

.. literalinclude:: ./assets/Donator.sol
   :language: solidity


Save the code to ``contracts/Donator.sol``.


Quick Solidity Overview
-----------------------

**Pragma**:
Every Solidity source should provide the compiler compatability: `pragma solidity ^0.4.11;`

**Contract definition**:
The ``contract`` keyword starts a new contract definition, named ``Donator``.

.. note::

    Contracts names should follow class naming rules (like MyWallet, GoodLuck or WhyNot).

**State variables**:
The contract has 4 state variables: ``donationsTotal``, ``donationsUsd``, ``donationsCount`` and ``defaultUsdRate``.
A state variable is defined in the *contract scope*.
State variables are saved in the contract's persisten *storage*,
kept after the transaction run ends, and synced to every node on the blockchain.

**Visibility:**
The ``public`` decleration ensures that all state variables and the ``donate`` function will be available for the callers
of the contrat, in the contract's interface.

.. note::
    For the public state variables, the compiler actually creates an accessor function
    which if you had to type manually could look like: ``function total() public returns (uint) {return donationsTotal;}``

**Data types**:
Since we are dealing with numbers, the only data type we use here is ``uint``, unsigned integer. The ``int`` and ``uint``
are declated in steps of 8 bits, ``unint8``, ``uint16`` etc. When the bits indicator is omitted, like ``int`` or ``uint``, the compiler will
assumes ``uint256``.

.. note::

    If you know in advance the the maximum size of a variable, better to limit the type and save the gas of extra
    memory or storage.

As of version 0.4.17 Solidity does *not* support decimal point types. If you need decimal point, you will have to manauly handle
the fixed point calculations with integers. For the sake of simplicty, the example uses only ints.


**Constructor**:
The function ``function Donator()`` is a constructor. A constructor function's name is always identical to the contract's name.
It runs once, when the contract is created, and can't be called again. Here we set the ``defaultUsdRate``, to be used
when the donator didn't provide the effective exchange rate. Providing a constructor function is optional.


**Functions**:
The ``donate`` function accepts one argument: ``usd_rate``. Then the function
updates the total donated, both of Ether and USD value. It also updates the default USD rate and the donations counter.

**Magic Variables**:
In every contract you get three magic variables in the global scope: ``msg``, ``block`` and ``tx``. You can use these
variable without prior decleration or assignment. To find out how much
Ether was sent, use ``msg.value``.

**Modifiers**:
``modifier nonZeroValue() { if (!msg.value > 0) throw; _; }``. The term "modifier" is a bit confusing.
A modifier of a function is  *another* function that injects, or modifies, code, typically to verify some pre-existing condition.
Since the donate function uses the modifier ``function donate(uint usd_rate) public payable nonZeroValue {...}``,
then ``nonZeroValue`` will run *before* ``donate``. The code in ``donate`` will run only if ``msg.value > 0``, and make sure
that the ``donationsCount`` does not increase by a zero donation.

.. note::

    The modifier syntax uses ``_;`` to tell solidity where to insert the *modified* function.
    We can of course check the include the modifier condition the original function, but a declared modifier is handy
    when you want to use the same pre-condition validation in more than one function.

.. _fallback_func:

**Fallback**:
The weired function without a name, ``function () payable {...}``, is the "fallback". It calls ``donate``, so when somebody just
send Ether to the contract address without explicitly call ``donate``, we can still accept the Ether. A fallback function
is what the contract runs when called *without an explicit function name*. This happens (a) when you call a contract
with  ``address.call``, and (b) when just send just Ether, in a transaction that don't call anything.

.. note::

    If a contract has a fallback function,
    any transaction or sending of ether to an address with code will result in it's code being invoked.

**Payable**:
``function donate(uint usd_rate) public payable nonZeroValue {...}`` and ``function () payable {...}`` use the *payable*
builtin modifier, in order to accept Ether. Otherwise, without this modifier, a transaction that sends Ether will fail.
If none of the contract functions has a ``payable`` modifier, the contract can't accept Ether.

**Initial Values**:
Note that ``donationsTotal += msg.value;`` was used before any assignment to ``donationsTotal``. The variables are auto initiated
with default values.


Side Note
---------

This Donator example is fairly simple.

If you are following the Ethereum world for a while, you probably noticed that many Ethereum projects are much more complex.
People and companies try to use contracts to manage distributed activity among very large groups,
assuming you need special, usually complex, code and strategies that defend against bad actores.
Some noticeable initiatives are the decentrelized autonomous organizations (DAO),
getting groups decisions where the voting rights are proportional to the Ether the voter sent to the contract,
or crowd funding with Ether, initial coin offerings (ICO),
feeds that send the contract up-to-date data from the "outside world", etc.

Don't let these projects intimidate you.

If you have a simple Ethereum based idea that is useful,
even for you personally, or to family and friends, go ahead and implement it. A small group of people that already know each other and
**trust** each other don't need the complex overhead. Just make sure the contract code is correct. You can do really nice things,
some are not possible without Ethereum.

We would be delighted to hear how it worked!


Interim Summary
---------------

So far you have:

* Initiated a project
* Initiated a local blockchain
* Added a new contract

Great. Next step is compiling and first deployment.

