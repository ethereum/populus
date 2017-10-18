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

This argument is provided in the test as *Python* donate function:

.. code-block:: python

    donator.transact({'value':650}).donate(380).

Populus gives you a *Python* interface to a bytecode contract. Nice, no?

**[6] Asserts**: We expect the ``donations_total`` to be ``500 + 650 = 1150``, the ``donations_count`` is 2,
and the ``default_usd_rate`` to match the last update, 380.

The test gets the varaibles with ``call``, and should update instanrly because it's a local ``tester`` chain. On a distributed
blockchain it will take sometime until the transactions are mined and actually change the state.

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


Test Calculations
-----------------


The next one will test the ETH/USD calculations:

.. code-block:: shell

    $ nano tests/test_donator.py

Add the following test to the bottom of the file:

.. code-block:: python

    def test_usd_calculation(chain):

        ONE_ETH_IN_WEI = 10**18  # 1 ETH == 1,000,000,000,000,000,000 Wei

        donator, deploy_tx_hash = chain.provider.get_or_deploy_contract('Donator')
        donator.transact({'value':ONE_ETH_IN_WEI}).donate(400)
        donator.transact({'value':(2 * ONE_ETH_IN_WEI)}).donate(500)
        donations_usd = donator.call().donations_usd()

        # donated 1 ETH in  $400 per ETH = $400
        # donated 2 ETH in $500 per ETH = 2 * $500 = $1,000
        # total $ value donated = $400 + $1,000 = $1,400
        assert donations_usd == 1400

The test sends donations worth of 3 Ether. Reminder: by default, all contract functions
and contract interactions are handled in *Wei*.

In 1 Ether we have 10^18 Wei (see the `Ether units denominations <http://ethdocs.org/en/latest/ether.html>`_)

The test runs two transactions: note the ``transact`` function, which will change the contract state and balance
on the blockchain. We use the ``tester`` chain, so the state is reset on each test run.

**First transaction**

.. code-block:: python

    donator.transact({'value':ONE_ETH_IN_WEI}).donate(400)

Donate Wei worth of 1 Ether, where the effective ETH/USD rate is $400. That is, $400 per Ether,
and a total *USD* value of $400

**Second transaction**

.. code-block:: python

    donator.transact({'value':(2 * ONE_ETH_IN_WEI)}).donate(500)

Donate Wei worth of *2* Ether, where the effective ETH/USD rate is $500. Wow, seems that the markets run for Eth!
It's $500 per Ether, and total *USD* value of 2 * $500 = $1,000

Hence we excpect the total *USD* value of these two donations to be $400 + $1,000 = $1,400

.. code-block:: python

    donations_usd = donator.call().donations_usd()
    assert donations_usd == 1400


OK, that wan't too complicated. Run the test:

.. code-block:: shell

    $ py.test --disable-pytest-warnings


And the py.test results:

.. code-block:: shell

    platform linux -- Python 3.5.2, pytest-3.1.3, py-1.4.34, pluggy-0.4.0
    rootdir: /home/mary/projects/donations, inifile:
    plugins: populus-1.8.0, hypothesis-3.14.0
    collected 3 items

    tests/test_donator.py ..F

    ================================ FAILURES =======================================================
    __________________________ test_usd_calculation _________________________________________________

    chain = <populus.chain.tester.TesterChain object at 0x7f2736d1c630>

        def test_usd_calculation(chain):

            ONE_ETH_IN_WEI = 10**18  # 1 ETH == 1,000,000,000,000,000,000 Wei

            donator, deploy_tx_hash = chain.provider.get_or_deploy_contract('Donator')
            donator.transact({'value':ONE_ETH_IN_WEI}).donate(400)
            donator.transact({'value':(2 * ONE_ETH_IN_WEI)}).donate(500)
            donations_usd = donator.call().donations_usd()

            # donated 1 ETH at $400 per ETH = $400
            # donated 2 ETH at $500 per ETH = 2 * $500 = $1,000
            # total $ value donated = $400 + $1,000 = $1,400
    >       assert donations_usd == 1400
    E       assert 1400000000000000000000 == 1400

    tests/test_donator.py:32: AssertionError
    ======================================= 1 failed, 2 passed, 15 warnings in 0.95 seconds =========


Ooops. Something went wrong. But this is what tests are all about.

Py.test tells us that the assert failed. Instead of 1,400, the ``donations_usd`` is 1400000000000000000000.
And you know the saying: a billion here, a billion there, and pretty soon you're talking about real money.

Where is the bug? you maybe guessed it already, but let's take a look at the contract's ``donate`` function:

.. code-block:: solidity

    function donate(uint usd_rate) public payable money_sent {
        donations_total += msg.value;
        donations_count += 1;
        default_usd_rate = usd_rate;
        uint in_usd = msg.value * usd_rate;
        donations_usd += in_usd;
        }

Now it's clear:

.. code-block:: solidity

    uint in_usd = msg.value * usd_rate;

This line multiplies ``msg.value``, which is in Wei, by ``usd_rate``, which is the exchange rate per *Ether*.

Reminder: as of 0.4.17 Solidity does not have a workable decimal point calculation, and you have to handle fixed-point
with integers. For the sake of simplicity, we will stay with ints.

Edit the contract:

.. code-block:: shell

    $ nano contracts/Donator.sol


And fix the line to:

.. code-block:: solidity

    uint in_usd = msg.value * usd_rate / 10**18;

Run the tests again:


.. code-block:: shell

    $ py.test --disable-pytest-warnings

    ==================================== test session starts ===================
    platform linux -- Python 3.5.2, pytest-3.1.3, py-1.4.34, pluggy-0.4.0
    rootdir: /home/mary/projects/donations, inifile:
    plugins: populus-1.8.0, hypothesis-3.14.0
    collected 3 items

    tests/test_donator.py ...

    ============================== 3 passed, 15 warnings in 0.93 seconds =======


Easy.

.. warning::

    Note that if this contract was running on ``mainent``, you could not fix it, and probably had
    to deploy a new one and loose the current contract and the money paid for it.
    This is why testing *beforehand* is so important
    with smart contracts.

Interim Summary
---------------

    * Three tests pass
    * Transactions tests pass
    * Exchange rate calculations pass
    * You fixed a bug in the contract source code.


The contract seems Ok, but to be on the safe side, we will run next a few tests for the edge cases.























