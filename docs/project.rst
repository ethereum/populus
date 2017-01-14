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

When instantaited with no arguments, the project will look for a ``populus.json``
file found in the current working directory and load that if found.


.. code-block::

    from populus.project import Project
    # loads local `populus.json` file (if present)
    project = Project()

    # loads the specified config file
    other_project = Project('/path/to/other/populus.json'])



Loading, Reloading, and Writing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:attribute:: Project.config_file_path

    The path to that configuration file that was loaded or ``None`` if no
    configuration file is present.


.. py:method:: Project.load_config()

    Loads the the project configuration from disk.


.. py:method:: Project.write_config()

    Writes the current project configuration to disk.  Writes to
    ``Project.config_file_path`` or ``project.json`` if
    ``Project.config_file_path`` is ``None``.


Filesystem Path Properties and Methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Populus exposes properties and methods to access the the various filesystem
dictories and paths that populus uses.


.. py:attribute:: Project.project_dir

    The path that populus will treat as the root of your
    project.  This defaults to the current working directory.


.. py:attribute:: Project.contracts_dir

    The path under which populus will search for contracts to compile.


.. py:attribute:: Project.build_dir

    The path that populus will place it's build artifacts from compilation.


.. py:attribute:: Project.compiled_contracts_file_path

    The path that the JSON build artifact will be written to.


.. py:attribute:: Project.compile_project_contracts

    The parsed JSON output loaded from the
    ``Project.compiled_contracts_file_path``.


.. py:method:: Project.get_chain(chain_name, *chain_args, *chain_kwargs)

    Returns the ``populus.chain.Chain`` instance associated with the geven
    ``chain_name``.  The ``chain_args`` and ``chain_kwargs`` are passed through
    to the constructor of the underlying ``populus.chain.Chain`` object.
