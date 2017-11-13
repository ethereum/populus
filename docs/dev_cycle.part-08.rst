Part 8: Web3.py Console
=======================

.. contents:: :local:


Geth Console in Python
----------------------

You have probably stumbled already with the term "geth console". Geth exposes a javascript
console with the Web3 javascript API, which is handy when you need an interactive
command-line access to geth and the running node. It's also a great way to tinker
with the blockchain.

Good news: you have identical interactive console with Python.
All you have to do is to initiate a Web3.py connection in a Python shell, and from
that point forward you have the exact same Web3 interface in Python.

We will show here only a few examples to get you going. Web3 is a comprehensive and
rich API to the Ethereum platform, and you probably want to familiarise yourself with it.

Almost any Web3.js javascript API has a *Pythonic* counterpart in Web3.py.

See the the `Web3.py documentation <https://web3py.readthedocs.io/en/latest/>`_ and
the `full list of `web3.js JavaScript API <https://web3js.readthedocs.io/en/1.0/>`_.


Web3.py Connection to Geth
--------------------------

Start with the ``horton`` local chain. Run the chain:

.. code-block:: shell

    $ chains/horton/./run_chain.sh

Start a Python shell:

.. code-block:: shell

    $ python

.. note::

    You may need  ``$ python3``


Initiate a Web3 object:

.. code-block:: shell

    >>> from web3 import Web3, IPCProvider
    >>> w3 = Web3(IPCProvider(ipc_path="/home/mary/projects/donations/chains/horton/chain_data/geth.ipc"))
    >>> w3
    >>> <web3.main.Web3 object at 0x7f29dcc7c048>


That's it. You now have a full Web3 API access in Python.

.. note::

    Use the actual path to the ``horton`` ipc_path. If you are not sure, look at the run file
    argument at ``chains/horton/run_chain.sh``.

Sidenote, this is a good example why geth uses IPC (inter-process communication).
It allows other *local* processes to access the running node. Web3, as another process, hooks to this IPC endpoint.

Console Interaction with a Contract Instance
--------------------------------------------

We can interact with a contract instance via the Python shell as well. We will do things in a bit convuluted manual way here,
for the sake of demostration. During the regular development process, Populus does all that
for you.

To get a handle to the ``Donator`` instance on ``horton`` we need (a) it's **address**, where the bytecode sits,
and (b) the **ABI** ,application binary interface, the detailed description of the functions and arguments
of the contract interface. With the ABI the EVM knows how to call the compiled
bytecode.

.. warning::

    A reminder, even when you call a contract without an ABI, or just send it Ether, you may still invoke
    code execution. The EVM will call the :ref:`fallback function <fallback_func>`, if it exists in the contract

First, the address. In another terminal window:

.. code-block:: shell

    $ cat registrar.json

The :ref:`populus_registrar` is where Populus holds the deployment details:

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

It's hard to tell which blockchain is ``horton``. Populus encodes a blockchain signature
by the *hash* of it's block 0.  We only see that ``Donator`` is deployed on two blockchains.

But since ``Greeter`` was deployed only on ``horton``,
the blockchain with two deployments is ``horton``, and the other one is ``morty``.
So we can tell that ``Donator`` address on ``horton`` is
``"0xb8d9d2afbe18fd6ac43042164ece9691eb9288ed"``.

Copy the actual address from your registrar file. Back in the python shell terminal, paste it:

.. code-block:: python

    >>> address = "0xb8d9d2afbe18fd6ac43042164ece9691eb9288ed"


Now we need the ABI. Go to the other terminal window:

.. code-block:: shell

    $ solc --abi contract/Donator.sol
    ======= contracts/Donator.sol:Donator =======
    Contract JSON ABI
    [{"constant":true,"inputs":[],"name":"donationsCount","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"donationsUsd","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"defaultUsdRate","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"donationsTotal","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"usd_rate","type":"uint256"}],"name":"donate","outputs":[],"payable":true,"type":"function"},{"inputs":[],"payable":false,"type":"constructor"},{"payable":true,"type":"fallback"}]

Copy only the long list ``[{"constant":true,"inputs":[]....]``, get back to the python shell,
and paste the abi inside single quotes, like ``'[...]'`` as follows:

.. code-block:: python

    >>> abi_js = '[{"constant":true,"inputs":[],"name":"donationsCount","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"donationsUsd","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"defaultUsdRate","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"donationsTotal","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"usd_rate","type":"uint256"}],"name":"donate","outputs":[],"payable":true,"type":"function"},{"inputs":[],"payable":false,"type":"constructor"},{"payable":true,"type":"fallback"}]'


Your python shell should look like this:

.. code-block:: python

    >>> from web3 import Web3, IPCProvider
    >>> w3 = Web3(IPCProvider(ipc_path="/home/mary/projects/donations/chains/horton/chain_data/geth.ipc"))
    >>> w3
    >>> <web3.main.Web3 object at 0x7f29dcc7c048>
    >>> address = "0xb8d9d2afbe18fd6ac43042164ece9691eb9288ed"
    >>> abi_js = '[{"constant":true,"inputs":[],"name":"donationsCount","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"donationsUsd","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"defaultUsdRate","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"donationsTotal","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"usd_rate","type":"uint256"}],"name":"donate","outputs":[],"payable":true,"type":"function"},{"inputs":[],"payable":false,"type":"constructor"},{"payable":true,"type":"fallback"}]'


From now on, we will stay in the python shell.

Solc produced the ABI in JSON. Convert it to Python:

.. code-block:: python

    >>> import json
    >>> abi = json.loads(abi_js)

Ready to instanciate a contract *object*:

.. code-block:: python

    >>> donator = w3.eth.contract(address=address,abi=abi)
    >>> donator
    <web3.contract.Contract object at 0x7f3b285245f8>

You now have the familiar ``donator`` Python object, with Python methods, that corresponds to a deployed contract
instance bytecode on a blockchain.

Let's verify it:

.. code-block:: python

    >>> donator.call().donationsCount()
    4
    >>> donator.call().donationsTotal()
    8000000000000000000

Works.

Btw, everything you did so far you can do in Populus with *one* line of code:

.. code-block::  python

    donator, deploy_tx_hash = chain.provider.get_or_deploy_contract('Donator')

When you work with Populus, you don't have to mess with the ABI.
Populus saves the ABI with other important compilation info at ``build/contracts.json``,
and grabs it when required, gets the Web3 handle to the chain, creates the contract
object and returns it to you (and if the contract is not deployed, it will deploy it).

.. warning::

    Worth to remind again. **Never** call a contract with just an address and an ABI. You never know
    what the code at that address does behind the ABI. The only safe way is either if you
    absolutly know and trust the author, or to check it yourself.
    Get the source code from the author, make sure the source is safe, then compile it yourself,
    and verify that the compiled bytecode
    on your side is **exactly the same** as the bytecode at the said address on the blockchain.


Note that ``donationsTotal`` is *not* the account balance as it is saved in the *blockchain* state.
It's rather a *contract* state. If we made a calculation mistake with ``donationsTotal`` then it won't
reflect the actual Ether balance of the contract.

So all these doantions are not in the balance? Let's see:

.. code-block:: python

    >>> w3.eth.getBalacne(donator.address)
    8000000000000000000

Phew. It's OK. The ``donationsTotal`` is exactly the same as the "official" balance.

And in Ether:

.. code-block:: python

    >>> w3.fromWei(w3.eth.getBalance(donator.address),'ether')
    Decimal('8')

How much is left in your coinbase account on ``horton``?

.. code-block:: python

    >>> w3.fromWei(w3.eth.getBalance(w3.eth.coinbase),'ether')
    Decimal('1000000026682')

Oh. This is one of those accounts where it's fun to check the balance, isn't it?

So much Ether! why not donate some? Prepare a transaction:

.. code-block:: python

    >>> transaction = {'value':5*(10**18),'from':w3.eth.coinbase}

Only 5 Ether. Maybe next time. Reminder: The default unit is always Wei, and 1 Ether == 10 ** 18 Wei.

Send the transaction, assume the effective ETH/USD exchange rate is $7 per Ether:

.. code-block:: python

    >>> donator.transact(transaction).donate(7)
    '0x86826ad2df93ffc6d6a6ac94dc112a66be2fff0453c7945f26bcaf20915058f9'

The hash is the *transaction's* hash. On local chains
transactions are picked and mined in seconds, so we can expect to see the changed state almost
immidiately:

.. code-block:: python

    >>> donator.call().donationsTotal()
    13000000000000000000
    >>> donator.call().defaultUsdRate()
    7
    >>> w3.fromWei(w3.eth.getBalance(donator.address),'ether')
    Decimal('13')

You can also send a transaction *directly* to the chain, instead of via the ``donator`` contract object.
It's a good opportunity, too, for a little more generousity. Maybe you go through the roof and donate
100 Ether!

.. code-block:: python

    >>> transaction = {'value':100*(10**18),'from':w3.eth.coinbase,'to':donator.address}
    >>> w3.eth.sendTransaction(transaction)
    >>> '0x395f5fdda0be89c803ba836e57a81920b41c39689ffefaaaaf6a30f532901bf5'


Check the state:

.. code-block:: python

    >>> donator.call().donationsTotal()
    113000000000000000000
    >>> donator.call().defaultUsdRate()
    7
    >>> w3.fromWei(w3.eth.getBalance(donator.address),'ether')
    Decimal('113')

Now pause for a moment. What just happened here? The transaction you just sent didn't call the ``donate`` function
at all. How did the donations total and balance increased? Take a look at the transaction again:

.. code-block:: python

    >>> transaction = {'value':100*(10**18),'from':w3.eth.coinbase,'to':donator.address}

No mention of the ``donate`` function, yet the 100 Ether were transfered and donated. How?

If you answered *fallback* you would be correct. The contract has a fallback function:

.. code-block:: solidity

    // fallback function
     function () payable {
       donate(defaultUsdRate);
     }

A :ref:`fallback function <fallback_func>` is the one un-named function you can optionally include in a contract. If it
exists, the EVM will call it when you just send Ether, without a function call. In ``Donator``,
the fallback just calls ``donate`` with the current ``defaultUsdRate``. This is why the balance
*did* increase by 100 Ether, but the ETH/USD rate didn't change
(there are also other options to invoke the fallback).

Unlike a transaction, ``call`` doesn't change state:

.. code-block:: python

    >>> transaction = {'value':50,'from':w3.eth.coinbase}
    >>>> donator.call(transaction).donate(10)
    []
    >>> w3.fromWei(w3.eth.getBalance(donator.address),'ether')
    >>> Decimal('113')
    >>> donator.call().defaultUsdRate()
    >>> 7

Console Interaction With Accounts
---------------------------------

List of accounts:

.. code-block:: python

    >>> w3.eth.accounts
    ['0x66c91389b47bcc0bc6206ef345b889db05ca6ef2']


Go to another terminal, in the shell:

.. code-block:: shell

    $ ls chains/horton/chain_data/keystore
    UTC--2017-10-19T14-43-31.487534744Z--66c91389b47bcc0bc6206ef345b889db05ca6ef2

The account hash in the file name should be the *same* as the one you have on the Python shell.
Web3 got the account from geth, and geth saves the accounts
as wallet files in the ''keystore`` directory.

.. note::

    The first part of the wallet file is a timestamp. See :ref:`tutorial_wallets`

Create a new account:

.. code-block:: python

    >>> w3.personal.newAccount()
    Warning: Password input may be echoed.
    Passphrase:demopassword
    Warning: Password input may be echoed.
    Repeat passphrase:demopassword

    '0x7ddb35e66679cb9bdf5380bfa4a7f87684c418d0'

A new account was created. In another terminal, in a shell:

.. code-block:: shell

    $ ls chains/horton/chain_data/keystore

    UTC--2017-10-19T14-43-31.487534744Z--66c91389b47bcc0bc6206ef345b889db05ca6ef2
    UTC--2017-10-21T14-08-01.257964745Z--7ddb35e66679cb9bdf5380bfa4a7f87684c418d0

The new wallet file was added to the chain keystore.

In the python shell:

.. code-block:: python

    >>> w3.eth.accounts
    ['0x66c91389b47bcc0bc6206ef345b889db05ca6ef2', '0x7ddb35e66679cb9bdf5380bfa4a7f87684c418d0']

Unlock this new account:

.. code-block:: python

    >>> w3.personal.unlockAccount(account="0x7ddb35e66679cb9bdf5380bfa4a7f87684c418d0",passphrase="demopassword")
    True

.. warning::

    Tinkering with accounts freely is great for development and testing.
    **Not** with real Ether. You should be extremely careful when you unlock an account with real Ether.
    Create new accounts with geth directly, so passwords don't appear in history.
    Use strong passwords, and the correct permissions. See :ref:`a_word_of_caution`



Getting Info from the Blockchain
--------------------------------

The Web3 API has many usefull calls to query and get info from the blockchain. All this information is publicly
available, and there are many websites that present it with a GUI, like `etherscan.io <https://etherscan.io/>`_.
The same info is available programmaticaly with Web3.

Quit the ``horton`` chain and start a new Python shell.

Mainnet with Infura.io
''''''''''''''''''''''

As an endpoint we will use ``infura.io``. It's a publicly avaialble blockchain node, by Consensys, which is great
for read-only queries.

Infura is a remote node, so you will use the ``HTTPProvider``.

.. note::
    Reminder: IPC, by design, allows only *local* processes to hook to the endpoint. Proccesses that
    run on the same machine. IPC is safer if you have to unlock an account,
    but for *read-only* queries remote HTTP is perfectly OK. Did we asked you already
    to look at :ref:`a_word_of_caution`? We thought so.

Start a Web3 connection.

.. code-block:: python

    >>> from web3 import Web3,HTTPProvider
    >>> mainent = Web3(HTTPProvider("https://mainnet.infura.io"))
    >>> mainent
    <web3.main.Web3 object at 0x7f7d3fb71fd0>

Nice. You have an access to the entire blockchain info at yor fingertips.


Get the last block:

.. code-block:: python

    >>> mainent.eth.blockNumber
    4402735

Get the block itself:

.. code-block:: python

    >>> mainent.eth.getBlock(4402735)
    AttributeDict({'mixHash': '0x83a49ac6843 ... })

The number of transactions that were included in this block:

.. code-block:: python

    >>> mainent.eth.getBlockTransactionCount(4402735)
    58

The hash of the first transaction in this block:

.. code-block:: python

    >>> mainent.eth.getBlock(4402735)['transactions'][0]
    '0x03d0012ed82a6f9beff945c9189908f732c2c01a71cef5c453a1c22da7f884e4'

This transaction details:

.. code-block:: python

    >>> mainent.eth.getTransaction('0x03d0012ed82a6f9beff945c9189908f732c2c01a71cef5c453a1c22da7f884e4')
    AttributeDict({'transactionIndex': 0, 'to': '0x34f9f3a0e64ba ... })

.. note::

    If you will use block number 4402735, you should get **exactly** the same output as shown above.
    This is the ``mainent``, which is synced accross all the nodes, and every node will return the same info.
    The local chains ``horton`` or ``morty`` run a private instance, so every machine produces it's own blocks and hashes.
    Not so on the global, real blockchain, where all the nodes are synced
    (which is the crux of the whole blockchain idea).



Testnet with Infura.io
''''''''''''''''''''''

Web3 exposes the API to the testnet, just by using a different url:

.. code-block:: python

    >>> from web3 import Web3,HTTPProvider
    >>> testnet = Web3(HTTPProvider("https://ropsten.infura.io"))
    >>> testnet
    <web3.main.Web3 object at 0x7ff597407d68>
    >>> testnet.eth.blockNumber
    1916242


Mainnet and Testnet with a Local Node
'''''''''''''''''''''''''''''''''''''

In order to use Web3.py to access the ``mainnet`` simply run geth on your machine:

.. code-block:: shell

    $ geth

When geth starts, it provides *a lot* of info. Look for the line ``IPC endpoint opened:``, and use this IPC endpoint path
for the Web3 IPCProvider.

In a similar way, when you run:

.. code-block:: shell

    $ geth --testnet

You will see another ipc path, and hooking to it will open a Web3 instance to the ``testnet``.


.. note::

    When you run geth for the first time, syncing can take time. The best way is to just to let geth run without
    interuption until it synced.

.. note::

    Geth keeps the accounts in the ``keystore`` directory for each chain. If you want to use the same account,
    you will have to copy of import the wallet file. See `Managing Accounts in geth <https://github.com/ethereum/go-ethereum/wiki/Managing-your-accounts>`_


Interim Summary
---------------

* Interactive Web3 API in a Python shell
* Interacting with a contract instance in the Python shell
* Managing accounts in the Python shell
* Query the blockchain info on ``mainnet`` and ``testnet`` with HTTP from a remote node
* Query the blockchain info on local geth nodes.

Although Populus does a lot of work behind the scenes, it's recommended to have a good grasp of Web3.
See the the `Web3.py documentation <https://web3py.readthedocs.io/en/latest/>`_ and
the `full list of `web3.js JavaScript API <https://web3js.readthedocs.io/en/1.0/>`_. Most of the javascript
API have a Python equivalent.










