.. _chain-wait:

Wait API
--------

.. module:: populus.wait
.. currentmodule:: populus.wait

.. py:class:: populus.wait.Wait(web3, timeout=empty, poll_interval=empty)


Each chain object exposes the following API through a property
:ref:`Chain.wait <chain-api-wait>`.  

* The ``timeout`` parameter sets the default number of seconds that each method will block before raising a :class:`~populus.utils.compat.Timeout` exception.  
* The ``poll_interval`` determines how long it should wait between polling.  If ``poll_interval == None`` then ``random.random()`` will be used to determine the poling interval.


.. py:method:: Wait.for_contract_address(txn_hash, timeout=120, poll_interval=None)

    Blocks for up to ``timeout`` seconds returning the contract address from the
    transaction receipt for the given ``txn_hash``.


.. py:method:: Wait.for_receipt(txn_hash, timeout=120, poll_interval=None)

    Blocks for up to ``timeout`` seconds returning the transaction receipt for
    the given ``txn_hash``.


.. py:method:: Wait.for_block(block_number=1, timeout=120, poll_interval=None)

    Blocks for up to ``timeout`` seconds waiting until the highest block on the
    current chain is at least ``block_number``.


.. py:method:: Wait.for_unlock(account=web3.eth.coinbase, timeout=120, poll_interval=None)

    Blocks for up to ``timeout`` seconds waiting until the account specified by
    ``account`` is unlocked.  If ``account`` is not provided,
    ``web3.eth.coinbase`` will be used.


.. py:method:: Wait.for_peers(peer_count=1, timeout=120, poll_interval=None)

    Blocks for up to ``timeout`` seconds waiting for the client to have at
    least ``peer_count`` peer connections.


.. py:method:: Wait.for_syncing(timeout=120, poll_interval=None)

    Blocks for up to ``timeout`` seconds waiting the chain to begin syncing.
