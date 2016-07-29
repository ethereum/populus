Deploy
~~~~~~

.. code-block:: shell

    $ populus deploy --help
    Usage: populus deploy [OPTIONS] [CONTRACTS_TO_DEPLOY]...

      Deploys the specified contracts via the RPC client.

    Options:
      -d, --dry-run                  Do a dry run deploy first.  When doing a
                                     production deploy, you should always do a dry
                                     run so that deploy gas prices can be known.
      -n, --dry-run-chain-name TEXT  Specifies the chain name that should be used
                                     for the dry run deployment.  Defaults to
                                     'default'
      -p, --production               Deploy to a production chain (RPC server must
                                     be run manually)
      --confirm / --no-confirm       Bypass any confirmation prompts
			--record / --no-record         Record the created contracts in the
			                               'known_contracts' lists. This only works for
																		 non-production chains.
      --help                         Show this message and exit.

Running ``$ populus deploy`` will deploy all specifed contracts to either the
default test chain or to a running JSON-RPC server depending on whether
``--production`` was specified.

If the ``--dry-run`` flag is specified, then the gas value supplied for each
contract's deployment will be determined based on how much gas was used during
the dry run deployment.

When using the ``--production`` flag populus will not run the JSON-RPC for you.
You are expected to have an RPC server running with an unlocked account.  Doing
a production deploy without ``--dry-run`` is not advisable.  Doing a dry run
ensures that all of your contracts are deployable as well as allowing the
production deployment to supply gas values determined from the dry run
deployments.

.. note::
    When using libraries, populus will try to link your libraries.  This
    functionality is experimental and could still have bugs.
