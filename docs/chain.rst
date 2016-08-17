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

Here is an example how to have your own py.test fixture for launching
a temporary Geth instance with a fresh blockchain.

See

* :py:meth:`populus.project.Project.get_chain`

* :py:class:`populus.project.Project`

* :py:class:`populus.chain.TemporaryGethChain`

* :py:class:`populus.config.Config`

* :py:class:`web3.Web3`

Example:

.. code-block:: python

    import os

    from populus.project import Project
    from populus.utils.config import Config
    from web3 import Web3
    from web3 import RPCProvider


    @pytest.yield_fixture(scope="session")
    def web3() -> Web3:
        """A py.test fixture to get a Web3 interface to a temporary geth instance.

        This is session scoped fixture.
        Geth is launched only once during the beginning of the test run.

        Geth will have a huge premined instant balance on its coinbase account.
        Geth will also mine our transactions on artificially low difficulty level.

        :yield: :py:class:`web3.Web3` instance
        """

        project = Project()

        # Project is configured using populus.config.Config class
        # which is a subclass of Python config parser.
        # Instead of reading .ini file, here we dynamically
        # construct the configuration.
        project.config = Config()

        # Settings come for [populus] section of the config.
        project.config.add_section("populus")

        # Configure where Populus can find our contracts.json
        build_dir = os.path.join(os.getcwd(), "websauna", "wallet", "ethereum")
        project.config.set("populus", "build_dir", build_dir)

        chain_kwargs = {

            # Force RPC provider instead of default IPC one
            "provider": RPCProvider,

            # Adjust geth verbosity for less
            # output so that test failures are easier to read.
            "verbosity": "2"
        }

        # This returns TemporaryGethChain instance as geth_proc
        with project.get_chain("temp", **chain_kwargs) as geth_proc:

            web3 = geth_proc.web3

            # Allow access to sendTransaction() to use coinbase balance
            # to deploy contracts. Password is from py-geth
            # default_blockchain_password file. Assume we don't
            # run tests for more than 9999 seconds
            coinbase = web3.eth.coinbase
            success = web3.personal.unlockAccount(
                coinbase,
                passphrase="this-is-not-a-secure-password",
                duration=9999)

            assert success, "Could not unlock test geth coinbase account"

            yield web3
