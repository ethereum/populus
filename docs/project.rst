Project
=======

.. contents:: :local:

.. module:: populus.project
.. currentmodule:: populus.project

Introduction
------------

.. py:class:: BaseChain

The :class:`~Project` class is the primary entry point to all aspects of
your populus project.


Basic Usage
-----------

- ``Project(config_file_path=None)``

When instantaited with no arguments, the project will look for a ``populus.json``
file found in the current working directory and load that if found.


.. code-block:: python

    from populus.project import Project
    # loads local `populus.json` file (if present)
    project = Project()

    # loads the specified config file
    other_project = Project('/path/to/other/populus.json')


The project object is the entry point for almost everything that populus can do.


.. code-block:: python

    >>> project.project_dir
    '/path/to/your-project`
    >>> project.contracts_dir
    './contracts'
    >>> project.config
    {....}  # Your project configuration.
    >>> project.compiled_contract_data
    {
      'Greeter': {
        'code': '0x...',
        'code_runtime': '0x...',
        'abi': [...],
        ...
      },
      ...
    }
    >>> with p.get_chain('temp') as chain:
    ...     print(chain.web3.eth.coinbase)
    ...
    0x4949dce962e182bc148448efa93e73c6ba163f03


Configuration
-------------

.. py:attribute:: Project.config

    Returns the current project configuration.


.. py:method:: Project.load_config()

    Loads the project configuration from disk, populating :attr:`Project.config`.


.. py:method:: Project.write_config()

    Writes the current project configuration from :attr:`Project.config` to disk.


Chains
------

.. py:method:: Project.get_chain(chain_name, chain_config=None)``

    Returns a ``populus.chain.Chain`` instance.  You may provide
    ``chain_config`` in which case the chain will be configured using the
    provided configuration rather than the declared configuration for this
    chain from your configuration file.

    The returned ``Chain`` instance can be used as a context manager.
