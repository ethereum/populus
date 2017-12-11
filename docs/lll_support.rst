LLL Support
===========

Populus provides partial support for LLL, in particular the
``lllc`` compiler, which is currently maintained in tandem
with Solidity in the `ethereum/solidity`_ repository.

.. _ethereum/solidity: https://github.com/ethereum/solidity

Known limitations
-----------------

This feature is highly experimental; mixing different languages,
e.g. Solidity and LLL or Viper and LLL, is not yet possible.

Since LLL is very low-level, not all language constructs are
currently supported. In particular, string literals, especially
defined with the ``lit`` keyword, may be impossible to use.

Finally, LLL programs have no notion of ``web3`` ABI, as detailed
in the `Ethereum Contract ABI`_ specification. For that reason,
all ``.lll`` files must have an accompanying ``.lll.abi`` file,
specifying in JSON the on-chain contract's interface.

.. _Ethereum Contract ABI: https://github.com/ethereum/wiki/wiki/Ethereum-Contract-ABI


Installation
------------

On Ubuntu-based systems, the ``lllc`` compiler seems to no longer
be available in a package. You might need to `build it from source`_.

For Ubuntu 14.04, one might be shipped together with ``solc``,
available in ``solidity-ubuntu-trusty.zip`` on the `releases page`_.


On Arch Linux, an ``lll`` package is `available in AUR`_.

In general, ``lllc`` should be available in ``PATH``; or an
``LLLC_BINARY`` environment variable must be set and pointing to
the ``lllc`` executable.

To see if it's present:

.. code-block:: shell

    $ lllc --version
    LLLC, the Lovely Little Language Compiler
    Version: 0.4.19-develop.2017.12.1+commit.c4cbbb05.Linux.g++

.. _build it from source: https://media.consensys.net/installing-ethereum-compilers-61d701e78f6
.. _releases page: https://github.com/ethereum/solidity/releases
.. _available in AUR: https://aur.archlinux.org/packages/lll/


Using
-----

Automatic initialisation of a ``Greeter`` project in LLL with
``populus --init`` is not yet possible.

This section describes how to do it manually.

Change compilation backend
^^^^^^^^^^^^^^^^^^^^^^^^^^

The compilation backend must be changed from its default in `project.json`
by placing a `backend` key in the `compilation` section, as shown below:

.. code-block:: json

    {
        "version": "7",
        "compilation": {
            "contracts_source_dirs": ["./contracts"],
            "import_remappings": [],
            "backend": {
                "class": "populus.compilation.backends.LLLBackend"
            }
        }
    }

Populus will now only compile LLL contracts in the configured ``contracts``
directories.

Copy LLL-specific Greeter contract and its ABI specification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These files should be available in the `Populus repository`_, as
`Greeter.lll`_ and `Greeter.lll.abi`_.

Place them in the ``contracts`` directory of your project.

.. _Populus repository: https://github.com/ethereum/populus
.. _Greeter.lll: https://github.com/ethereum/populus/tree/master/populus/assets
.. _Greeter.lll.abi: https://github.com/ethereum/populus/tree/master/populus/assets/Greeter.lll.abi

Copy LLL-specific test
^^^^^^^^^^^^^^^^^^^^^^

This file should be available in the `Populus repository`_, as
`test_greeter_lll.py`_.

Place it in the ``tests`` directory of your project.

Remove the Solidity/Viper ``test_greeter.py`` if it's still present, so
``pytest`` doesn't trip.

.. _test_greeter_lll.py: https://github.com/ethereum/populus/tree/master/populus/assets/test_greeter_lll.py
