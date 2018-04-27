Part 10: Dependencies
=====================

.. contents:: :local:



So far we have worked with, and deployed, one contract at a time.
However, Solidity allows you to inherit
from other contracts, which is especially useful when you a more generic functionality in
a basic core contract, a functionality you want to inherit and re-use in another, more specific use case.


A Contract that is Controlled by it's Owner
-------------------------------------------


The ``Donator2`` contract is better than ``Donator``, because it allows to withdraw the donations that the contract accepts.
But not much better: at any given moment *anyone* can withdraw the entire donations balance, no questioned asked.

If you recall the withdraw function from the contract:

.. code-block:: solidity

  //demo only allows ANYONE to withdraw
  function withdrawAll() external {
      require(msg.sender.send(this.balance));
        }

The ``withdrawAll`` function just sends the entire balance, ``this.balance``,
to whoever request it. Send everything to ``msg.sender``, without any further verification.

A better implementation would be to allow **only the owner of the contract to withdraw the funds**. An *owner*, in the Ethereum
world, is an *account*. An *address*. The owner is the account that the contract creation transaction was sent from.

Restricting permission to run some actions only to the owner is a very common design pattern.  There are many
open-source implementations of this pattern, and we will work here with the `OpenZeppelin <https://openzeppelin.org/>`_ library.

.. note::

  When you adapt an open sourced Solidity contract from github, or elsewhere, be careful. You should trust only
  respected, known authors, and always review the code yourself. Smart contracts can induce some smart bugs,
  which can lead directly to loosing money. Yes, the Ethereum platform has many innovations,
  but loosing money from software bugs is not one of them. However, it's not fun to loose Ether like this. Be careful from intentional or unintentional bugs.
  See some really clever examples in
  `Underhanded Solidity Coding Contest <https://medium.com/@weka/announcing-the-winners-of-the-first-underhanded-solidity-coding-contest-282563a87079>`_

This is the OpenZeppelin `Ownable.sol <https://github.com/OpenZeppelin/zeppelin-solidity/blob/master/contracts/ownership/Ownable.sol>`_ Contract:


.. literalinclude:: ./assets/Ownable.sol
   :language: solidity


Save it to your contracts directory:


.. code-block:: shell

  $ nano contracts Ownable.sol


Inheritance & Imports
---------------------

Create the new improved ``Donator3``:

.. literalinclude:: ./assets/Donator3.sol
   :language: solidity


Almost the same code of ``Donator2``, with 3 important additions:

**[1]** An import statement: ``import "./Ownable.sol" ``: Used to when you use constructs
from other source files, a common practice in
almost any programming language. The format of local path with ``./Filename.sol``
is used for an import of a file in the same directory.

.. note::

  Solidity supports quite comprehensive import options. See the Solidity documentation
  of `Importing other Source Files <http://solidity.readthedocs.io/en/latest/layout-of-source-files.html#importing-other-source-files>`_

**[2]** Subclassing: ``contract Donator3 is Ownable {...}``

**[3]** Use a parent member in the subclass:

.. code-block:: solidity

  function withdrawAll() external onlyOwner {
        require(msg.sender.send(this.balance));
          }

The ``onlyOwner`` modifier was *not* defined in ``Donator3``, but it is inherited,
and thus can be used in the subclass.

Your contracts directory should look as follows:

.. code-block:: shell

  $ ls contracts
  Donator2.sol  Donator3.sol  Donator.sol  Greeter.sol  Ownable.sol

Compile the project:

.. code-block:: shell

  $ populus compile
  > Found 5 contract source files
  - contracts/Donator.sol
  - contracts/Donator2.sol
  - contracts/Donator3.sol
  - contracts/Greeter.sol
  - contracts/Ownable.sol
  > Compiled 5 contracts
  - contracts/Donator.sol:Donator
  - contracts/Donator2.sol:Donator2
  - contracts/Donator3.sol:Donator3
  - contracts/Greeter.sol:Greeter
  - contracts/Ownable.sol:Ownable

Compilation works, ``solc`` successfully found ``Ownable.sol`` and imported it.

Testing the Subclass Contract
-----------------------------

The test is similar to a regular contract test. All the parents' members are inherited and available for testing
(if a parent member was overridden, use ``super`` to access the parent member)

Add a test:

.. code-block:: shell

  $ nano tests/test_donator3.py

The test should look as follows:

.. code-block:: python

  import pytest
  from ethereum.tester import TransactionFailed

  ONE_ETH_IN_WEI = 10**18

  def test_ownership(chain):
      donator3, deploy_tx_hash = chain.provider.get_or_deploy_contract('Donator3')
      w3 = chain.web3
      owner = w3.eth.coinbase # alias

      # prep: set a second test account, unlocked, with Wei for gas
      password = "demopassword"
      non_owner =  w3.personal.newAccount(password=password)
      w3.personal.unlockAccount(non_owner,passphrase=password)
      w3.eth.sendTransaction({'value':ONE_ETH_IN_WEI,'to':non_owner,'from':w3.eth.coinbase})

      # prep: initial contract balance
      donation = 42 * ONE_ETH_IN_WEI
      effective_usd_rate = 5
      transaction = {'value': donation, 'from':w3.eth.coinbase}
      donator3.transact(transaction).donate(effective_usd_rate)
      assert w3.eth.getBalance(donator3.address) == donation

      # test: non owner withdraw, should fail
      with pytest.raises(TransactionFailed):
          donator3.transact({'from':non_owner}).withdrawAll()
      assert w3.eth.getBalance(donator3.address) == donation

      # test: owner withdraw, ok
      donator3.transact({'from':owner}).withdrawAll()
      assert w3.eth.getBalance(donator3.address) == 0

The test is similar to the previous tests. Py.test and the Populus plugin provide
a ``chain`` fixture, as an argument to the test function which is a handle to the ``tester`` ephemeral chain.
``Donator3`` is deployed, and the test function gets a contract object to ``donator3``.

Then the test creates a second account, ``non_owner``, unlocks it, and send to this account 1 Ether to pay for the gas.
Next, send 42 Ether to the contract.

.. note::

  The test was deployed with the default account, the ``coinbase``. So ``coinbase``, or the alias
  ``owner``, is the owner of the contract.

When the test tries to withdraw with ``non_owner``, which is *not* the owner, the transaction fails:

.. code-block:: python

      # test: non owner withdraw, should fail
      with pytest.raises(TransactionFailed):
          donator3.transact({'from':non_owner}).withdrawAll()
      assert w3.eth.getBalance(donator3.address) == donation


When the owner tries to withdraw it works, and the balance is back to 0:

.. code-block:: python

      # test: owner withdraw, ok
      donator3.transact({'from':owner}).withdrawAll()
      assert w3.eth.getBalance(donator3.address) == 0

Run the test:

.. code-block:: shell

  $ py.test --disable-pytest-warnings

  ===================================== test session starts ======================
  platform linux -- Python 3.5.2, pytest-3.1.3, py-1.4.34, pluggy-0.4.0
  rootdir: /home/mary/projects/donations, inifile: pytest.ini
  plugins: populus-1.8.0, hypothesis-3.14.0
  collected 5 items

  tests/test_donator.py ....
  tests/test_donator3.py .
  =========================== 5 passed, 24 warnings in 3.52 seconds ==============


Passed.

The 2nd test will test the``Ownable`` function that allows to transfer ownership. Only the current owner
can run it. Let's test it.

Edit the test file:

.. code-block:: shell

  $ nano tests/test_donator3.py

And add the following test function:


.. code-block:: python


  def test_transfer_ownership(chain):
      donator3, deploy_tx_hash = chain.provider.get_or_deploy_contract('Donator4')
      w3 = chain.web3
      first_owner = w3.eth.coinbase # alias

      # set unlocked test accounts, with Wei for gas
      password = "demopassword"
      second_owner =  w3.personal.newAccount(password=password)
      w3.personal.unlockAccount(second_owner,passphrase=password)
      w3.eth.sendTransaction({'value':ONE_ETH_IN_WEI,'to':second_owner,'from':w3.eth.coinbase})

      # initial contract balance
      donation = 42 * ONE_ETH_IN_WEI
      effective_usd_rate = 5
      transaction = {'value': donation, 'from':w3.eth.coinbase}
      donator3.transact(transaction).donate(effective_usd_rate)
      assert w3.eth.getBalance(donator3.address) == donation

      # test: transfer ownership
      assert donator3.call().owner == first_owner
      transaction = {'from':first_owner}
      donator3.transact(transaction).transferOwnership(second_owner)
      assert donator3.call().owner == second_owner

      # test: first owner withdraw, should fail after transfer ownership
      with pytest.raises(TransactionFailed):
          donator3.transact({'from':first_owner}).withdrawAll()
      assert w3.eth.getBalance(donator3.address) == donation

      # test: second owner withdraw, ok after transfer ownership
      donator3.transact({'from':second_owner}).withdrawAll()
      assert w3.eth.getBalance(donator3.address) == 0

      # test: transfer ownership by non owner, should fail
      transaction = {'from':first_owner}
      with pytest.raises(TransactionFailed):
          donator3.transact(transaction).transferOwnership(second_owner)
      assert donator3.call().owner == second_owner


Run the test:

.. code-block:: shell

  $ py.test --disable-pytest-warnings

The test should fail:

.. code-block:: shell

            # transfer ownership
  >       assert donator3.call().owner == first_owner
  E       AssertionError: assert functools.partial(<function call_contract_function at 0x7f6245b39bf8>, <web3.contract.PopulusContract object at 0x7f624466e748>, 'owner', {'to': '0xc305c901078781c232a2a521c2af7980f8385ee9'}) == '0x82a978b3f5962a5b0957d9ee9eef472ee55b42f1'


Yes. ``donator3.call().owner`` is wrong. Confusing. Reminder: ``owner`` should be accessed as a *function*,
and *not* as a property, The compiler builds these functions for every public state variable.

Fix every occurrence of ``call().owner`` to ``call().owner()``. E.g., into:

.. code-block:: python

  assert donator3.call().owner() == first_owner


Then Run again:

.. code-block:: shell

  $ py.test --disable-pytest-warnings

Fails again:

.. code-block:: shell

            # test: transfer ownership
  >       assert donator3.call().owner() == first_owner
  E       AssertionError: assert '0x82A978B3f5...f472EE55B42F1' == '0x82a978b3f59...f472ee55b42f1'
  E         - 0x82A978B3f5962A5b0957d9ee9eEf472EE55B42F1
  E

In the Ethereum world, it does not matter if an address is uppercase or lowercase (capitalisation is used for checksum,
to avoid errors in client applications). We will use all lower case.

Fix the test as follows:

.. code-block:: python

  def test_transfer_ownership(chain):
      donator3, deploy_tx_hash = chain.provider.get_or_deploy_contract('Donator4')
      w3 = chain.web3
      first_owner = w3.eth.coinbase # alias

      # set unlocked test accounts, with Wei for gas
      password = "demopassword"
      second_owner =  w3.personal.newAccount(password=password)
      w3.personal.unlockAccount(second_owner,passphrase=password)
      w3.eth.sendTransaction({'value':ONE_ETH_IN_WEI,'to':second_owner,'from':w3.eth.coinbase})

      # initial contract balance
      donation = 42 * ONE_ETH_IN_WEI
      effective_usd_rate = 5
      transaction = {'value': donation, 'from':w3.eth.coinbase}
      donator3.transact(transaction).donate(effective_usd_rate)
      assert w3.eth.getBalance(donator3.address) == donation

      # test: transfer ownership
      assert donator3.call().owner().lower() == first_owner.lower()
      transaction = {'from':first_owner}
      donator3.transact(transaction).transferOwnership(second_owner)
      assert donator3.call().owner().lower() == second_owner.lower()

      # test: first owner withdraw, should fail after transfer ownership
      with pytest.raises(TransactionFailed):
          donator3.transact({'from':first_owner}).withdrawAll()
      assert w3.eth.getBalance(donator3.address) == donation

      # test: second owner withdraw, ok after transfer ownership
      donator3.transact({'from':second_owner}).withdrawAll()
      assert w3.eth.getBalance(donator3.address) == 0

      # test: transfer ownership by non owner, should fail
      transaction = {'from':first_owner}
      with pytest.raises(TransactionFailed):
          donator3.transact(transaction).transferOwnership(second_owner)
      assert donator3.call().owner().lower() == second_owner.lower()


Run the test:

.. code-block:: shell

  $ py.test --disable-pytest-warnings

  ================================================== test session starts ==============
  platform linux -- Python 3.5.2, pytest-3.1.3, py-1.4.34, pluggy-0.4.0
  rootdir: /home/may/projects/donations, inifile: pytest.ini
  plugins: populus-1.8.0, hypothesis-3.14.0
  collected 6 items

  tests/test_donator.py ....
  tests/test_donator3.py ..

  ========================================== 6 passed, 29 warnings in 1.93 seconds ====


Ok, all the inherited members passed: The ``Ownable`` constructor that sets ``owner`` ran when you deployed
it's subclass, ``Donator3``. The parent modifier ``onlyOwner`` works as a modifier to a subclass function,
and the ``transferOwnership`` parent's function can be called by clients via the subclass interface.

.. note::

  If you will deploy ``Donator3`` to a local chain, say ``horton``, and look at the ``registrar.json``, you
  will not see an entry for ``Ownable``. The reason is that although Solidity has a full complex multiple inheritance
  model (and ``super``), the final result is once contract. Solidity just copies the inherited code to this contract.


Interim Summary
---------------

* You used an open sourced contract
* You imported one contract to another
* You added an ownership control to a contract
* You used inheritance and tested it
