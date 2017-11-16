Part 11: Events
===============

.. contents:: :local:


One of the things to get used to with Ethereum platform is the feedback loop. When you work
with a common Python project on your local machine, functions return in no time. When you call
a remote REST API, you response takes 1-2 seconds. When you send a transaction,
it's status is "pending", and you will have to wait until a miner picks it, include it in
a block, and the block is accepted by the blockchain. This can take a few minutes.

To track when a transaction is accepted, you use an ``event``. An event is a way to to write an indexable
log entry to the transaction reciept. Once the transaction is accepted, the receipt and the logs are included in the
block as well, and you can watch every new block until the log entry you are looking for appears.


