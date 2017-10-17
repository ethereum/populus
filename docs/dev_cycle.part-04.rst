Part 4: Transaction Tests
=========================

.. contents:: :local:

Test a Contract Function
------------------------

Edit the tests file and add another test:

.. code-block:: shell

    $ nano contracts/test_donator.py
    
After the edit, the file should look as follows:

.. code-block:: python


    def test_default_usd_rate(chain):
        donator, deploy_tx_hash = chain.provider.get_or_deploy_contract('Donator')
        default_usd_rate = donator.call().default_usd_rate()
        assert default_usd_rate == 350
        
        
    def test_donate(chain):    
        donator, deploy_tx_hash = chain.provider.get_or_deploy_contract('Donator')
        donator.transact({'value':500}).donate(370)
        donator.transact({'value':650}).donate(380)
        donations_count = donator.call().donations_count()
        donations_total = donator.call().donations_total()
        default_usd_rate = donator.call().default_usd_rate()
        
        assert donations_total == 1150
        assert donations_count == 2
        assert default_usd_rate == 380


You added another test, ``test_donations``. The second test is similar to the first one: 

**[1] Get the chain**: The test function accepts the ``chain`` argument, the auto-generated Python object that
corresponds to a ``tester`` chain. Reminder: the ``tester`` chain is ephimeral, in memory, and reset
on each test function.

**[2] Get the contract**: With the magic function ``get_or_deploy_contract`` Populus compiles the `Donator` contract,
deploys it to the ``chain``, creates a Web3 ``contract`` object, and returns it to the function as a Python
object with Python methods. This object is stored in the ``donator`` variable.

**[3] The "transact" function**:

.. code-block:: python

    donator.transact({'value':500}).donate(370)
    
Reminder: we have two options to interact with a contract on the blockchain, *transactions* and *calls*.
With Populus, you initiate a transaction with ``transact``, and a call with ``call``:

* *Transactions*: Send a transaction, run the contract code, transfer funds, and *change* the state of the contract and it's balance. This change will be permenant, and synced to the entire blockchain.

* *Call*: Behaves exactly as a transaction, but once done, everything is revert and no state is changed. A call is kinda "dry-run"


**[4] Test transactions**: The test commits two transactions, and send funds in both. In the first the ``value`` of the funds is 500,
and in the second the ``value`` is 650.
The ``value`` is provided as a ``transact`` argument, in a dictionary, where you can add more kwargs of an Ethereum 
transaction.


.. note:: 

    Since these are *transactions*, they will change state, and in the case of the ``tester`` chain this state will persist
    until the test function quits.


**[5] Providing arguments**: The donate function in the contract accepts one argument

.. code-block:: solidity

    function donate(uint usd_rate) public payable money_sent {...}
    
This argument is provided in  a *Python* donate function: ``donator.transact({'value':650}).donate(380)``. Populus gives you *Python* interface to a bytecode
contract. Nice, no?

**[6] Asserts**: We expect the ``donations_total`` to be ``500 + 650 = 1150``, the ``donations_count`` is 2,
and the ``default_usd_rate`` to match the last update, 380. The test gets the varaibles with ``call``, but in the case
of a "getter" it does not matter, since a "getter" function will not change state wether it's calls with ``transact`` or ``call``.

Run the test:

.. code-block:: bash

    $ py.test --disable-pytest-warnings
    
    platform linux -- Python 3.5.2, pytest-3.1.3, py-1.4.34, pluggy-0.4.0
    rootdir: /home/mary/projects/donations, inifile:
    plugins: populus-1.8.0, hypothesis-3.14.0
    collected 2 items 
    
    tests/test_donator.py ..
    
    ===================== 2 passed, 10 warnings in 0.58 seconds =============
        
Voila. The two tests pass.















