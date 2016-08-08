Chain management
================

Managing blockchains from command line
--------------------------------------

Populus provides a wrapper around ``geth`` to facilitate management of
ephemeral test chains.  These commands are accessed through ``$ populus chain``

The blockchains that populus manages for you are stored in ``./chains`` in the
projec root.  All ``chain`` commands will operate on the 'default' chain.  You
can specify alternate chains by adding a name to the end of the command.

Each blockchain will have one account generated for it.

* ``$ populus chain run`` - Run a geth node backed by the 'default' test chain.
* ``$ populus chain run test1`` - Run a geth node backed by the 'test1' test
  chain which will be stored at ``./chains/test1/`` relative to your project
  root.
* ``$ populus chain reset`` - Reset the 'default' chain (truncates the
  blockchain, preserves accounts)
* ``$ populus chain reset test01`` - Reset the 'test1' chain (truncates the
  blockchain, preserves accounts)

Programmatically launching a new chain
--------------------------------------

To run a private chain on your local computer see :py:func:`populus.chain.testing_geth_process`.

