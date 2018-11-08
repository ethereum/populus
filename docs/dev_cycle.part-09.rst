Part 9: Withdraw Money from a Contract
======================================

.. contents:: :local:


Well, time to get out some of the donations, for a good cause!


Available Balance
-----------------

First, we will check the balanc. The balance of an Ethereum account
is saved as a blockchain status for an *address*, wether that address has a contract or not.

In addition to the "official" balance,
the contract manages a ``total_donations`` state variable that should be the same.


We will query both. Add the following script:

.. code-block:: shell

    $ nano scripts/donator_balance.py

The script should look as follows:

.. code-block:: python

    from populus.project import Project

    p = Project(project_dir="/home/mary/projects/donations/")
    with p.get_chain('horton') as chain:
        donator, _ = chain.provider.get_or_deploy_contract('Donator')

    # state variable
    donationsTotal = donator.call().donationsTotal()

    # access to Web3 with the chain web3 property
    w3 = chain.web3

    # the account balance as saved by the blockchain
    donator_balance = w3.fromWei(w3.eth.getBalance(donator.address),'ether')

    print (donationsTotal)
    print (donator_balance)


The script is very similar to what you already done so far. It starts with a ``Project``
object which is the main entry point to the Populus API. From the project
we get the chain, and a contract object.
Then the script grabs the ``donationsTotal`` with a ``call``, no need for a transaction.
Finally, with the Web3 API, we get the contract's balance as it is saved on the chain.

Both ``donationsTotal`` and the balance are in Wei. The web3 API ``fromWei`` converts it to Ether.

Two things to notice. A minor style change:

.. code-block:: python

    donator, _ = chain.provider.get_or_deploy_contract('Donator')

Instead of:

.. code-block:: python

     donator, deploy_tx_hash = chain.provider.get_or_deploy_contract('Donator')

We know that the contract is already deployed, so the return tuple from ``get_or_deploy_contract``
for an *already deployed* contract is ``(contract_obj, None)``.

Second thing to notice, is that the Populus API gives you access the entire Web3 API, using the
``chain.web3`` property.

Run the script:

.. code-block:: shell

    $ python scripts/donator_balance.py
    113000000000000000000
    113


Withdraw Funds from a Contract
------------------------------

Can you guess the correct way to *withdraw* Ether from ``Donator``?
You can dig a little into what you have done so far.

(we are waiting, it's OK)

Have an idea? Any suggestion will do.

(still waiting, np)

You don't have a clue how to withdraw the donations from the contract, do you?

It's OK. Neither do we.


The contract has **no** method to *withdraw* the Ether. If you, as the contract author, don't implement a way to withdraw funds
or send them to another account, there is **no built in way to release the money**.  The Ether is stucked on the contract
balance forever. As far as the blockchain is concerned, those 113 Ether will remain in the balance of the ``Donator``
address, and you will not be able to use them.

Can you fix the code and redeploy the contract? Yes. But it will not release those 113 Ether. The new fixed contract
will be deployed to a **new address**, an address with zero balance. The 113 lost Ether are tied to the **old address**.
On the Ethereum blockchain, the smart contract's bytecode is tied to a *specific* address,
and the funds that the contract holds are tied to the *same address*.

Unlike common software code, the smart contract is *stateful*. The
code is saved with a state. And this state is synced to the entire network. The state can't be changed without a proper transaction,
that is valid, mined, included in a block, and accepted by the network. Without a way to accept a transaction that releases funds,
the ``Donator`` will just continue to hold these 113 Ether. In other words, they are lost.

.. note::

    The blockchain "state" is not a physical property of nature. The state is a consensus
    among the majority of the nodes on the blockchain. If, theoreticaly, all the nodes decide to wipe out an account
    balance, they can do it. A single node can't, but the entire network can. It's unlikely to happen, but it's
    a theoretical possiblility you should be aware of. It happend once, after the DAO hack, where all the nodes
    agreed on a *hard fork*, a forced update of the blockchain state, which reverted the hack.
    See `a good discussion of the issue on Quartz <https://qz.com/730004/everything-you-need-to-know-about-the-ethereum-hard-fork/>`_.




Withdraw Funds from a Contract, Take 2
--------------------------------------

Don't sweat those lost Ether. After all, what are 113 dummy Ethers out of a billion something Ether
in your local ``horton`` chain. With the ``horton`` chain, you can absolutly afford it. And if it will
prevent you from loosing real Ether on ``mainent`` in the future, then the cost/utility ratio of this lesson is excellent. Wish we could
pay for more lessons with dummy Ether, if we were asked (but nobody is asking).

Anyway. Let's move on to a fixed contract with an option to withdraw the funds.

Create a new contract:

.. code-block:: shell

        $ nano contracts/Donator2.sol

The new contract should look as follows:

.. literalinclude:: ./assets/Donator2.sol
   :language: solidity


Withdraw is handled in one simple function:

.. code-block:: solidity

      //demo only allows ANYONE to withdraw
      function withdrawAll() external {
          require(msg.sender.send(this.balance));
            }

Anyone that calls this function will get the entire Ether in the contract to his or her own
account. The contract sends its remaining balance, ``this.balance``, to the account address
that sent the transaction, ``msg.sender``.

The send is enclosed in a ``require`` clause, so if something failed everything is reverted.

.. warning::

    This is a very naive way to handle money, only for the sake of demonstration.
    In the next chapter we will limit the withdrwal only to the contract owner.
    Usually contracts keep track of beneficiaries and the money they are allowed
    to withdraw.

Re-entry attack
''''''''''''''''

When ``Donator2`` will run ``send(this.balance)``, the beneficiary
contract gets an opportunity to run its ``fallback`` and get the execution control.
In the fallback, it can call ``Donator2`` again before the ``send`` was line was completed, but the money already *sent*.
This is a *re-entry* attack. To avoid it, any state changes should occur *before* the send.

.. code-block:: solidity

      //demo only allows ANYONE to withdraw
      function withdrawAll() external {
          // update things here, before msg.sender gets control
          // if it re-enters, things already updated
          require(msg.sender.send(this.balance));
          // if you update things here, msg.sender get the money from the send
          // then call you, but things were not updated yet!
          // your contract state will not know that it's a re-entry
          // and the money was already sent
            }

To summarise, if you need to update state variables about sending money,
do it *before* the send.

Deploy Donator2
'''''''''''''''

Ok. Ready for deployment  (probably much less mysterious by now):

.. code-block:: shell

    $ chains/horton/./run_chain.sh

    INFO [10-22|01:00:58] Starting peer-to-peer node

In another terminal:

.. code-block:: shell

    $ populus compile
    > Found 3 contract source files
      - contracts/Donator.sol
      - contracts/Donator2.sol
      - contracts/Greeter.sol
    > Compiled 3 contracts
      - contracts/Donator.sol:Donator
      - contracts/Donator2.sol:Donator2
      - contracts/Greeter.sol:Greeter
    > Wrote compiled assets to: build/contracts.json

Compilation passed. Deploy:

.. code-block:: shell

    $ populus depoly --chain horton Donator2 --no-wait-for-sync

    Donator2
    Deploy Transaction Sent: 0xc34173d97bc6f4b34a630db578fb382020f092cc9e7fda20cf10e897faea3c7b
    Waiting for confirmation...


    Transaction Mined
    =================
    Tx Hash      : 0xc34173d97bc6f4b34a630db578fb382020f092cc9e7fda20cf10e897faea3c7b
    Address      : 0xcb85ba30c0635872774e74159e6e7abff0227ac2
    Gas Provided : 319968
    Gas Used     : 219967


Deployed to ``horton`` at ``0xcb85ba30c0635872774e74159e6e7abff0227ac2``.

Add a simple script that queries the ``Donator2`` instance on ``horton``:


.. code-block:: shell

    $ nano contracts/donator2_state.py

The script should look as follows:

.. code-block:: python

    from populus.project import Project

    p = Project(project_dir="/home/mary/projects/donations/")
    with p.get_chain('horton') as chain:
        donator2, _ = chain.provider.get_or_deploy_contract('Donator2')

    donationsCount = donator2.call().donationsCount()
    donationsTotal = donator2.call().donationsTotal()
    donationsUsd = donator2.call().donationsTotal()
    w3 = chain.web3
    balance = w3.fromWei(w3.eth.getBalance(donator2.address),'ether')

    print("donationsCount {:d}".format(donationsCount))
    print("donationsTotal {:d}".format(donationsTotal))
    print("donationsUsd {:d}".format(donationsUsd))
    print("balance {:f}".format(balance))

Again, we use the Populus API to get a handle to the ``Project``,
and with a project object we can get the chain, the contract object, and the
web3 connection.

Run the script:

.. code-block:: shell

    $ python scripts/donator2_state.py

    donationsCount 0
    donationsTotal 0
    donationsUsd 0
    balance 0.000000


Nice new blank slate contract, with zero donations.
Told you: those 113 Ether in ``Donator`` are lost

Add another script that donates 42 Ether to ``Donator2``. To be precise, to the ``Donator2``
instance on ``horton``:

.. code-block:: shell

    $ nano scripts/donator2_send_42eth.py


And you could probably write the script yourself by now:

.. code-block:: python

    from populus.project import Project

    p = Project(project_dir="/home/mary/projects/donations/")
    with p.get_chain('horton') as chain:
        donator2, _ = chain.provider.get_or_deploy_contract('Donator2')

    ONE_ETH_IN_WEI = 10**18
    effective_eth_usd_rate = 5
    transaction = {'value':42 * ONE_ETH_IN_WEI, 'from':chain.web3.eth.coinbase}
    tx_hash = donator2.transact(transaction).donate(effective_eth_usd_rate)
    print (tx_hash)

Save the script and run it 3 times:

.. code-block:: shell

    $ python scripts/donator2_send_42eth.py
    0xd3bbbd774bcb1cd72fb4b5823c71c5fe0b2efa84c5eeba4144464d95d810a353
    $ python scripts/donator2_send_42eth.py
    0xbc20f92b2940bdecb9aac7c181480647682218b552a7c96c4e72cf93b237160c
    $ python scripts/donator2_send_42eth.py
    0x43b99aa89af1f5596e5fa963d81a57bfe0c9da0100c9f4108540a67c57be0c93

Check state:

.. code-block:: shell

    $ python scripts/donator2_state.py
    donationsCount 0
    donationsTotal 0
    donationsUsd 0
    balance 0.000000

Still nothing. Wait a few seconds, then try again:

.. code-block:: shell

    $ python scripts/donator2_state.py
    donationsCount 3
    donationsTotal 126000000000000000000
    donationsUsd 630
    balance 126


Ok. All the three transactions where picked and mined by the chain.

A Transaction to Withdraw Ether to a New Account
------------------------------------------------

Open a Python shell and create a new account:

.. code-block:: python

    >>> from populus.project import Project
    >>> p = Project(project_dir="/home/mary/projects/donations/")
    >>> with p.get_chain('horton') as chain:
    ...     donator2, _ = chain.provider.get_or_deploy_contract('Donator2c')
    >>> w3 = chain.web3
    >>> w3.personal.newAccount()
    Warning: Password input may be echoed.
    Passphrase:demopassword

    Warning: Password input may be echoed.
    Repeat passphrase:demopassword

    '0xe4b83879df1194fede2a95555576bbd33142c244'
    >>> new_account = '0xe4b83879df1194fede2a95555576bbd33142c244'

To withdraw money, the withdrawing account must send a transaction.
If successful, this transaction will change the state of the blockchain: the contract's account sends Ether,
another account recieves it.

The ``'from'`` key of the transaction will be this *new_account*, the withdrawer. Type:

.. code-block:: python

    >>> tx_withdraw = {'from':new_account}

Reminder. The following Solidity line in the contract will pick the sender,
and tell the EVM to send the balance to the account that sent the transaction:

.. code-block:: solidity

    require(msg.sender.send(this.balance));


Send the transaction:

.. code-block:: python

    >>> donator2.transact(tx_withdraw).withdrawAll()

    ...
    raise ValueError(response["error"])
    builtins.ValueError: {'message': 'insufficient funds for gas * price + value', 'code': -32000}


Right. The new account is obviously empty and doesn't have money for the gas:

.. code-block:: python

    >>> w3.eth.getBalance(new_account)
    0


Transfer one Ether from your billion something ``coinbase`` account to the new account:

.. code-block:: python

    >>> w3.eth.sendTransaction({'from':w3.eth.coinbase,'to':new_account,'value':10**18})
    '0x491f45c225e7ce22e8cf8289da392c4b34952101582b3b9c020d9ad5b6c61504'
    >>> w3.eth.getBalance(new_account)
    1000000000000000000

Great. Has more than enough Wei to pay for the gas.

.. note::

    This is exactly why you used ``--no-wait-for-sync`` on deployments. When the account has funds to pay
    for the gas, you don't have to sync. But when you work with ``mainnet`` and
    your local node is not synced, it may think that the account is empty, although some transactions in further blocks
    did send the account money. Once the local node is synced to this block, geth can use it to pay for gas.

Send the withdraw transaction again:

.. code-block:: python

    >>> donator2.transact(tx_withdraw).withdrawAll()

    ...
    raise ValueError(response["error"])
    builtins.ValueError: {'message': 'authentication needed: password or unlock', 'code': -32000}

Oops. Who said that withdrawing money is easy.

You created a new account but *didn't unlock* it. Geth can send transactions only with an *unlocked* account. It
needs the unlocked account to sign the transaction with the account's private key, otherwise the miners can't ensure
that the transaction was actually sent by the account that claims to send it.

Unlock the account:

.. code-block:: python

    >>> w3.personal.unlockAccount(new_account,passphrase="demopassword")

.. warning::

    Again, extremely naive and unsafe way to unlock and use passwords. Use only for development and testing,
    with dummy Ether

The new account should be ready. It's unlocked and has the funds for the gas.

Send the withdraw transaction yet *again*:


    >>> donator2.transact(tx_withdraw).withdrawAll()
    '0x27781b2b3a644b7a53681459081b998c42cfcf02d87d82c78dbb7d6119110521'
    >>> w3.eth.getBalance(new_account)
    126999489322000000000

Works. The geek shell inherit the earth.

Quit the Python shell, and check the contract's balance, or more precisely, the balance of the *address* of this contract *instance*:

.. code-block:: shell

    $ python scripts/donator2_state.py
    donationsCount 3
    donationsTotal 126000000000000000000
    donationsUsd 630
    balance 0.000000

Correct. The balance is 0, yet ``donationsTotal`` that saves a running total of the *accepted* donations, shows all the 3
accepted donations of 42 Ether each.

.. note::

    ``donationsTotal`` is a state variable that is saved in the *contract's* storage. The ``balance`` is the balance
    in Wei of the *address* of the contract, which is saved as part of the *blockchain's* status.

As an exercise, add some tests to test the ``withdrawAll`` functionality on ``Donator2``.


Interim Summary
---------------

* If an author of a contract didn't implement a way to withdraw Ether, there is no builtin way to do it, and any money that was sent to this contract is lost forever
* Fixing a contract source code and re-deploying it saves the new bytecode to a *new* address, and does *not* and can *not* fix an existing contract instance on a previously deployed address
* You just created a new account, unlocked it, and withdrew money to it, with a transaction to a contract instance on a local chain
* You used the Web3 API via the Populus API























