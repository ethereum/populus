.. _Project:

Project
-------

.. contents:: :local:

.. py:module:: populus
.. py:currentmodule:: populus


Introduction
^^^^^^^^^^^^

The Project API is the common entry point to all aspects of
your populus project.


Basic Usage
^^^^^^^^^^^

.. py:class:: Project(config_file_path=None)

When instantaited with no arguments, the project will look for the following
configuration files in the following order.

* ``populus.json``
* ``populus.yml``
* ``populus.ini``

If more than one of these files is present in the root of your project populus
will throw an exception indicating that you must consolodate your configuration
to a single file.

The ``populus.ini`` style configuration is deprecated as of ``1.4.2`` and
populus will refuse to update this type of configuration file as it must be
migrated to a ``json`` or ``yaml`` file type.


Loading, Reloading, and Writing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:attribute:: Project.config_file_path

    The path that configuration will be written to when
    ``Project.write_config()`` is called.  This defaults to a file named
    ``populus.json`` in directory ``Project.project_dir``.


.. py:method:: Project.load_config()

    Loads the project configuration from disk, replacing the current
    configuration for the project.  This occurs automatically during
    instantiation of the ``Project`` class.


.. py:method:: Project.write_config(destination_path=None)

    Writes the current project configuration to the file path denoted by
    ``Project.config_file_path``.  If no configuration file was specified
    during project instantiation which will typically be the case, this will
    default to writing to ``populus.json`` or ``populus.yml``.


Filesystem Path Properties and Methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Populus exposes properties and methods to access the the various filesystem
dictories and paths that populus uses.


.. py:attribute:: Project.project_dir

    The path that populus will treat as the root of your
    project.  This defaults to the current working directory.  It can be
    overridden in your ``populus.ini`` under the ``[populus]`` section with the
    option ``project_dir``.


.. py:attribute:: Project.contracts_dir

    The path under which populus will search for contracts to compile.
    Configurable under the path ``compilation.contracts_source_dir``.  Defaults
    to ``<project-dir>/contracts``.


.. py:attribute:: Project.build_dir

    The path that populus will place it's build artifacts from compilation.


.. py:attribute:: Project.compiled_contracts_file_path

    The path that the JSON build artifact will be written to.


.. py:attribute:: Project.compile_contracts

    The parsed JSON result from compilation.


.. py:method:: Project.get_chain(chain_name, *chain_args, *chain_kwargs)

    Returns the ``populus.chain.Chain`` instance associated with the geven
    ``chain_name``.  The ``chain_args`` and ``chain_kwargs`` are passed through
    to the constructor of the underlying ``populus.chain.Chain`` object.


.. py:attribute:: Project.blockchains_dir

    The path that the files for local blockchains will be placed.


.. py:method:: Project.get_blockchain_data_dir(chain_name)

    Return the data directory for the blockchain with the given name.


.. py:method:: Project.get_blockchain_chaindata_dir(chain_name)

    Returns the chaindata directory for the blockchain with the given name.


.. py:method:: Project.get_blockchain_ipc_path(chain_name)

    Returns the path to the ``geth.ipc`` socket for the blockchain with the
    given name.


.. py:attribute:: Project.migrations_dir

    The path that the project migration files are located.


.. py:attribute:: Project.migration_files

    A list of all of the file paths to the project migrations.


.. py:attribute:: Project.migrations

    A list of all of the project migration classes loaded from the
    ``Project.migration_files``.  The classes are returned ordered according to
    their declaired dependencies.
