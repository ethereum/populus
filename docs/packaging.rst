Configuration
=============

.. contents:: :local:


.. warning:: The packaging functionality is highly experimental.  All APIs are subject to change without notice.

Introduction
------------

Populus can be used as a package manager to interact with any ERC190 smart
contract packages.


Disclaimers and General Development Status
------------------------------------------

.. warning:: The packaging functionality is not safe enough for anything close to production use cases.

.. warning:: The packaging APIs are subject to change without notice.

You *should* be able to do the following things

- Install *any* valid release lockfile.
- Import contract sources from installed packages.
- Link against deployed instances of libraries from installed packages.
- Building source-only packages (packages which don't contain any deployed contract instances)
- Building packages with deployed instances on a single chain.
- Publishing release lockfiles.

The following things may not work at all or may only work specific conditions.

- Building packages with deployed instances from multiple chainls chains.
- Building packages with deployed instances of contracts from a dependency.
- Attempting to link against a deployed instance of a library from an installed package which itself has link dependencies from deployed instances of libraries from one of the installed package's installed packages.
- Compilation will fail if there are two libraries with the same name across any of the source files.
- Compilation does not respect declared compiler version for bytecode verification.

The following things are not yet implemented.

- Full bytecode verification through all dependencies.
- Friendly errors
- Friendly or detailed terminal output.


Project Manifest
----------------

In order to take advantage of the packaging features you will first need to
create a package manifest for your project.  This can either be done manually
or using the command line helper ``$ populus package init`` which will present
an interactive prompt for creating the ``epm.json`` file.


Installing Packages
-------------------

Packages can be installed using the ``$populus package install`` command.
Packages may be specified in the following formats.

* ``populus package install .``:

    To install all of the declared dependencies found within the project's package manifest.

* ``populus package install some-package-name``

    To install a named package ``some-package-name`` sourced from a package index.

* ``populus package install ipfs://QmUwVUMVtkVctrLDeL12SoeCPUacELBU8nAxRtHUzvtjND``

    To install directly from a release lockfile via IPFS

* ``populus package install /path/to/release-lockfile.json``

    To install directly from a release lockfile on the local filesystem.


Populus also supports installing packages under aliased names.  This can be
used to allow multiple versions of the same package to be installed in tandem.

* ``populus package install some-alias:some-package-name``

    To install a named package ``some-package-name`` under the name
    ``some-alias`` sourced from a package index.

* ``populus package install some-alias@ipfs://QmUwVUMVtkVctrLDeL12SoeCPUacELBU8nAxRtHUzvtjND``

    To install directly from a release lockfile via IPFS using the name ``some-alias``.

* ``populus package install some-alias@/path/to/release-lockfile.json``

    To install directly from a release lockfile on the local filesystem using
    the name ``some-alias``


Packages are installed in the ``./installed_packages`` directory in the root
project directory under their aliased name, or their package name if no alias
is used.

When a package is installed it is automatically saved to the project
dependencies within the package manifest.  This can be disabled by passing in
the ``--no-save`` flag during installation.

Using Contracts from Installed Packages
---------------------------------------

Importing a contract from an installed package is done by prefixing the source
path with the name of the installed package, or the alias name if an alias was
used.

Lets use the common *owned* pattern for an example.  Suppose we have the
``owned`` package installed in our project.  We know that this package has a
single solidity source file that contains the ``owned`` contract located at
``./contracts/owned.sol``.

To import a contract from this file into local solidity source files you would
simply prefix the import path with the package name.

.. code-block:: solidity

    pragma solidity ^0.4.0;

    import "owned/contracts/owned.sol";

    contract MyContract is owned {
        ...
    }

.. note:: If you install a package which either has source files which do not compile with the solidity compiler version you are using, or which have a ``pragma solidity`` statement which is incompatable with your version of solidity then compilation will fail.


Building and Publishing Releases
--------------------------------

TODO
