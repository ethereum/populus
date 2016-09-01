Release Notes
=============


1.0.0
-----

This is the first release of populus that should be considered stable.

* Remove ``$ populus web`` command
* Remove ``populus.solidity`` module in favor of ``py-solc`` package for
  solidity compilation.
* Remove ``populus.geth`` module in favor of ``py-geth`` for running geth.
* Complete refactor of pytest fixtures.
* Switch to ``web3.py`` for all blockchain interactions.
* Compilation:
  * Remove filtering.  Compilation now always compiles all contracts.
  * Compilation now runs with optimization turned on by default.  Can be
    disabled with ``--no-optimizie``.
  * Remove use of  ``./project-dir/libraries`` directory.  All contracts are
    now expected to reside in the ``./project-dir/contracts`` directory.
* New `populus.Project` API.
* New Migrations API:
  * ``$ populus chain init`` for initializing a chain with the Registrar contract.
  * ``$ populus makemigration`` for creating migration files.
  * ``$ populus migrate`` for executing migrations.
* New configuration API:
  * New commands ``$ populus config``, ``$ populus config:set`` and ``$ populus
    config:unset`` for managing configuratino.
* New Chain API:
  * Simple programatic running of project chains.
  * Access to ``web3.eth.contract`` objects for all project contracts.
  * Access to pre-linked code based on previously deployed contracts.
