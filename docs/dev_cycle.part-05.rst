Part 5: Edge Cases Tests
========================

.. contents:: :local:

Test a Modifier "throw" Exception
---------------------------------

In the contract we used a modifier, to enforce a pre-condition on the ``donate`` function:
A donation should not be of value 0, otherwise the modifier will ``throw``. We wanted this modifier
to make sure that the donations counter will not increment for zero donations:

.. code-block:: solidity

   modifier nonZeroValue() { if (!(msg.value > 0)) throw; _; }
   function donate(uint usd_rate) public payable nonZeroValue {...}


Edit the tests file:

.. code-block:: shell

    $ nano tests/test_donator.py

And add the following test to the bottom of the file:

.. code-block:: python

    import pytest
    from ethereum.tester import TransactionFailed


    def test_modifier(chain):

        donator, deploy_tx_hash = chain.provider.get_or_deploy_contract('Donator')
        with pytest.raises(TransactionFailed):
            donator.transact({'value':0}).donate(4)

        defaultUsdRate = donator.call().defaultUsdRate()
        assert defaultUsdRate == 350


Simple test. Note the py.test syntax for *expected* exceptions: ``with pytest.raises(...)``.

The test transaction is of 0 value:

.. code-block:: python

    donator.transact({'value':0}).donate(4)

So the modifier should ``throw``.

Since the transaction should fail, the ``defaultUsdRate`` should remain the same, with the original initialisation
of the constructor

.. code-block:: solidity

  function Donator() {
  defaultUsdRate = 350;
  }

And ignore the test transaction with ``.donate(4)``.

Run the tests:

.. code-block:: shell

    $ py.test --disable-pytest-warnings

    ===================================== test session starts ===============
    platform linux -- Python 3.5.2, pytest-3.1.3, py-1.4.34, pluggy-0.4.0
    rootdir: /home/mary/projects/donations, inifile:
    plugins: populus-1.8.0, hypothesis-3.14.0
    collected 4 items

    tests/test_donator.py ....

    ========================= 4 passed, 20 warnings in 1.07 seconds =========


Works, all 4 tests passed.

Fallback Function
-----------------

At the moment, Populus does not have a builtin option to call fallback function.
To run it, you can send a simple transaction with Web3, or even better: write another function that you can test,
and let the ``fallback`` only call this function

Interim Summary
---------------

    * Working Contract
    * All tests pass

The next step is to deploy the contract to a persisetent chain.




