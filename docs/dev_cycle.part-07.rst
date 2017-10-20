Part 7: Interacting With a Contract Instance
============================================

.. contents:: :local:

Python Objects for Contract Instances
-------------------------------------

A contract instance is a bytecode on the blockchain at a specific address. Populus and Web3 give you a Python object with Python methods,
which correspond to this bytecode. You interact with this local *Python* object, but behind the scenes these Python interactions
are sent to a the bytecode on the blockchain.

To find and interact with a contract on the blockchain, this local contract object needs an *address*
and the *ABI* (application binary interface).

Reminder: the contract instance is compiled, a bytecode, so the EVM
(ethereum virtual machine) needs the ABI in order to call this bytecode. The ABI (application binary interface)
is essentially a JSON file with detailed description of the functions and their arguments, which tells how to call them. It's part of the
compiler output.

Populus does not ask you for the address and the ABI of the projects' contracts:  it already
has the address in the :ref:`registrar <populus_registrar>` file at ``registrar.json``,
and the ABI in ``build/contracts.json``

However, if you want to interact with contract instances from other projects, or even deployed by others,
you will need to create a Web3 contract yourself and manually provide the address and the ABI.
See `Web3 Contracts <http://web3py.readthedocs.io/en/latest/contracts.html#contract-factories>`_

.. warning::

    When you call a contract that you didn't compile
    and didn't deploy yourself, you should be 100% sure that it's trusted, that the author is trusted, and only
    only after you got a version of the Solidity contract's source, and verified that the compilation
    of this source is *identical* to the bytecode on the blockchain.


Call an Instance Function
-------------------------

A ``call`` is a contract instance invocation that doesn't change
state. Since the state is *not* changed, there is no need to create a transaction, to mine the transaction into a block,
and to propagate it and sync to the entire blockchain. The ``call`` runs only on the one node you are connected to,
and the node reverts everything when the ``call`` is finished - and saves you the expensive gas.

Calls are useful to query an *existing* contract state, without any changes,
when a local synced node can just hand you this info. It's also useful as a "dry-run" for transactions: you run a ''call'', make sure
everything is working, then send the real transaction.

To access a conract function with ``call``, in the same way you have done with the tests,
use ``contract_obj.call().foo(arg1,arg2...)``
where ``foo`` is the contract function. Then ``call()`` returns an object that exposed the contract instance functions
in Python.

To see an example, edit the script:

.. code-block:: shell

    $ nano scripts/donator.py


And add a few lines, as follows:

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

    # Get contract state with calls
    donations_count = donator.call().donations_count()
    donations_total = donator.call().donations_total()

    # Client side
    ONE_ETH_IN_WEI = 10**18  # 1 ETH == 1,000,000,000,000,000,000 Wei
    total_ether = donations_total/ONE_ETH_IN_WEI
    avg_donation = donations_total/donations_count if donations_count > 0 else 0
    status_msg = (
        "Total of {:,.2f} Ether accepted in {:,} donations, "
        "an avergage of {:,.2f} Wei per donation."
        )

    print (status_msg.format(total_ether, donations_count, avg_donation))

Pretty much similar to what we did so far: The script starts with the ``Project`` object,
the main entry point to the Populus API. The project object provides a ``chain`` object (as long as
this chain is defined in the project-scope or user-scope configs),
and once you have the ``chain`` you can get the contract *instance* on that chain.

Then we get the ``donations_count`` and the ``donations_total`` with ``call``. Populus, via Web3, calls
the running geth node, and geth grabs and return these two state variables
from the contract's storage. Even if we had used geth as a node to ``mainnet``, a sync node can get this info
localy.

These are the same public variables that you declared in the ``Donator`` Solidity source:

.. code-block:: solidity

    contract Donator {

        uint public donations_total;
        uint public donations_usd;
        uint public donations_count;
        uint public default_usd_rate;

        ...
    }


Finally, we can do some client side processing.

Run the script:

.. code-block:: shell

    $ python scripts/donator.py

    Donator address on horton is 0xb8d9d2afbe18fd6ac43042164ece9691eb9288ed
    The contract is already deployed on the chain
    Total of 0.00 Ether accepted in 0 donations, an avergage of 0.00 Wei per donation.


Note that we don't need an expensive state variable
for "average", in the contract, nor a function to calculate average.
The contract just keeps only what can't be done elsewhere, to save gas. Moreover, code on deployed contracts can't be changed,
so offloading code to the client gives you a lot of flexibility (and, again, gas, if you need a fix and re-deploy).

Send a Transaction to an Instance Function
------------------------------------------

To change the *state* of the instance, ether balance and the state variables, you need to send a transaction.

Once the transaction is picked by a miner, included in a block and accepted by the blockchain, every node
on the blockchain will run and update the state of your contract. This process obviously costs real money,
the gas.

With Populus and Web3 you send transactions with the ``transact`` function. For every contract instance object,
``transact()`` exposes the contract's instance functions. Behind the scenes, Populus takes your Pythonic call and,
via Web3, convert it to the transactions' ``data`` payload, then sends the transaction to geth.

When geth get the transaction, it sends it to the blockchain. Populus will return the transaction hash.
and you will have to wait until it's mined and accepted in a block. Typically 1-2 seconds with a local chain,
but will take more time on ``testnet`` and ``mainnet`` (you will watch new blocks with ``filters`` and ``events``,later on that).

We will add a transaction to the script:

.. code-block:: bash

    $ nano scripts/donator.py

Update the script:

.. code-block:: python

    import random
    from populus.project import Project

    p = Project(project_dir="/home/mary/projects/donations/")
    with p.get_chain('horton') as chain:
        donator, deploy_tx_hash = chain.provider.get_or_deploy_contract('Donator')

    print("Donator address on horton is {address}".format(address=donator.address))
    if deploy_tx_hash is None:
        print("The contract is already deployed on the chain")
    else:
        print("Deploy Transaction {tx}".format(tx=deploy_tx_hash))

    # Get contract state with calls
    donations_count = donator.call().donations_count()
    donations_total = donator.call().donations_total()

    # Client side
    ONE_ETH_IN_WEI = 10**18  # 1 ETH == 1,000,000,000,000,000,000 Wei
    total_ether = donations_total/ONE_ETH_IN_WEI
    avg_donation = donations_total/donations_count if donations_count > 0 else 0
    status_msg = (
        "Total of {:,.2f} Ether accepted in {:,} donations, "
        "an avergage of {:,.2f} Wei per donation."
        )

    print (status_msg.format(total_ether, donations_count, avg_donation))

    # Donate
    donation = ONE_ETH_IN_WEI * random.randint(1,10)
    effective_eth_usd_rate = 5
    transaction = {'value':donation, 'from':chain.web3.eth.coinbase}
    tx_hash = donator.transact(transaction).donate(effective_eth_usd_rate)
    print ("Thank you for the donation! Tx hash {tx}".format(tx=tx_hash))


The transaction is a simple Python dictionary:

.. code-block:: python

    transaction = {'value':donation, 'from':chain.web3.eth.coinbase}

The ``value`` is obviously the amount you send *in Wei*, and the ``from`` is the account that sends the transaction.

.. note::

    You can include any of the ethereum allowed items in a transaction except ``data`` which is
    created auto by converting the Python call to an EVM call. Web3 also set 'gas' and 'gasPrice' for you
    based on estimates if you didn't provide any. The 'to' field, the instance address, is already known to Populus
    for project-deployed contracts. See `transaction parameters <https://github.com/ethereum/wiki/wiki/JavaScript-API#parameters-25>`_

**Coinbase Account**

Until now you didn't provide any account, because in the tests the ``tester`` chain magically creates and unlocks
ad-hoc accounts. With a *persistent* chain you have to explictly provide the account.

Luckily, when Populus created the local ``horton`` chain it also created a default wallet file, a password file that unlocks the wallet,
and included the ``--unlock`` and ``--password`` arguments for geth in the run script, ``run_chain.sh``. When you run
``horton`` with ``chains/horton/./run_chain.sh`` the account is already unlocked.

All you have to do is to say that you want this account as the transaction account:

.. code-block:: python

    'from':chain.web3.eth.coinbase

The ``coinbase`` (also called ``etherbase``) is the default account that geth will use. You can have as many accounts
as you want, and set *one* of them as a coinbase. If you didn't add an account for ``horton``, then the chain has only
one account, the one that Populus created, and it's automatically assigned as the coinbase.

.. note::

    The wallet files are saved in the chain's ``keystore`` directory. For more see the tutorial on :ref:`tutorial_wallets` and
    :ref:`tutorial_accounts`. For a more in-depth discussion see `geth accounts managment <https://github.com/ethereum/go-ethereum/wiki/Managing-your-accounts>`_


Finally, the script sends the transaction with ``transact``:

.. code-block:: python

    tx_hash = donator.transact(transaction).donate(effective_eth_usd_rate)



Ok. Run the script, after you make sure that ``horton`` is running:

.. code-block:: shell

    $ python scripts/donator.py

    Donator address on horton is 0xb8d9d2afbe18fd6ac43042164ece9691eb9288ed
    The contract is already deployed on the chain
    Total of 0.00 Ether accepted in 0 donations, an avergage of 0.00 Ether per donation.
    Thank you for the donation! Tx hash 0xbe9d182a508ec3a7efc3ada8cfb134647b39feec4a7eb018ef91cc38e216ddbc

Worked. The transaction was sent, yet we still don't see it. Run again:

.. code-block:: shell

    $ python scripts/donator.py

    Donator address on horton is 0xb8d9d2afbe18fd6ac43042164ece9691eb9288ed
    The contract is already deployed on the chain
    Total of 3.00 Ether accepted in 1 donations, an avergage of 3,000,000,000,000,000,000.00 Wei per donation.
    Thank you for the donation! Tx hash 0xf6d40adfedf1882e7543c4ef96803bd790127afdc67e40a4c7d91d29884ad182

First donation accepted! Run again:

.. code-block:: shell

    $ python scripts/donator.py

    Donator address on horton is 0xb8d9d2afbe18fd6ac43042164ece9691eb9288ed
    The contract is already deployed on the chain
    Total of 4.00 Ether accepted in 2 donations, an avergage of 2,000,000,000,000,000,000.00 Wei per donation.
    Thank you for the donation! Tx hash 0x21bd87b9db76b54a48c5a12a4bf7930a0e45480f5af5d0745cb2e8b4a438c5af

And they just keep coming.

If you looked at your geth chain terminal windown, you could see how geth picks the transaction
and mine it:

.. code-block:: shell

    INFO [10-20|01:48:32] 🔨 mined potential block                  number=3918 hash=d36ecd…e724c1
    INFO [10-20|01:48:32] Commit new mining work                   number=3919 txs=0 uncles=0 elapsed=1.084ms
    INFO [10-20|01:48:40] Submitted transaction                    fullhash=0xbe9d182a508ec3a7efc3ada8cfb134647b39feec4a7eb018ef91cc38e216ddbc recipient=0xb8d9d2afbe18fd6ac43042164ece9691eb9288ed
    INFO [10-20|01:49:05] Successfully sealed new block            number=3919 hash=4e36eb…01e41f
    INFO [10-20|01:49:05] 🔨 mined potential block                  number=3919 hash=4e36eb…01e41f
    INFO [10-20|01:49:05] Commit new mining work                   number=3920 txs=1 uncles=0 elapsed=735.282µs
    INFO [10-20|01:49:21] Successfully sealed new block

Check the persistancy of the instance again. Stop the ``horton`` chain, press Ctrl+C in it's terminal window,
and then re-run it with ``chains/horton/./run_chain.sh``.

Run the script again:

.. code-block:: shell

    $ python scripts/donator.py

    Donator address on horton is 0xb8d9d2afbe18fd6ac43042164ece9691eb9288ed
    The contract is already deployed on the chain
    Total of 7.00 Ether accepted in 3 donations, an avergage of 2,333,333,333,333,333,504.00 Wei per donation.
    Thank you for the donation! Tx hash 0x8a595949271f17a2a57a8b2f37f409fb1ee809c209bcbcf513706afdee922323

Oh, it's so easy to donate when a genesis block allocates you billion something.

The contract instance *is* persistent, and the state is saved. With ``horton``, a local chain, it's saved to your hard-drive.
On ``mainent`` and ``testnet``, to the entire blockchain nodes network.


.. note::

    You may have noticed that we didn't call the ``fallback`` function. Currently there is no builtin way to call
    the ``fallback`` from Populus. You can simply send a transaction to the contract instance's address,
    without any explicit function call. On transaction w/o a function call the EVM will call the ``fallback``.
    Even better, write another named function that you can call and test
    from Populus, and let the ``fallback`` do one thing - call this function.


Programatically Access to a Contract Instance
---------------------------------------------

The script is very simple, but it gives a glimpse how to use Populus as bridge between your Python application
and the Ethereum Blockchain. As an excercise, update the script so it prompts for donation amount, or work with
the ``Donator`` instance on the *morty* local chain.

This is another point that you'll appreciate Populus: not only it helps
to manage, develop and test blockchain assets (Solidity sources, compiled data, deployments etc),
but it also exposes your blockchain assets
as Python objects that you can later use *natively* in any of your Python projects. For more see #TODO Populus API.

Interim Summary
---------------

* You interacted with an Ethereum persistent contract instance on a local chain
* You used ``call`` to invoke the instance (no state change)
* You sent transactions to the instance (state changed)
* You used the ``Project`` object as an entry point to Populus' API for a simple Python script
* And, boy, you just donated a very generous amount of Wei.




