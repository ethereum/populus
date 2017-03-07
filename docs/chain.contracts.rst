.. _chain-contracts:

.. module:: populus.chain.base
.. currentmodule:: populus.chain.base

.. py:class:: BaseChain


Accessing Contracts
===================

The :class:`~populus.chain.base.BaseChain` object is the entry point for the Provider
and Registrar APIs which collectively give access to your project contracts and
related information.

* The Provider API gives access to both the raw compiler output, the contract factories and the deployed instances of your contracts.  This api can be accessed from the :attr:`BaseChain.provider` property.
* The Registrar API records the addresses of deployed contract instances for later retrieval.  This api can be accessed from the :attr:`BaseChain.registrar` property.


Getting the raw compiled data
-----------------------------

To retrieve the contract data for a specific contract you will use the
:meth:`BaseChain.provider.get_base_contract_factory` method.  Supposing that your
project contained a contract named "Math" you could retrieve the contract data
using the following code.

.. code-block:: python

    >>> chain.provider.get_base_contract_factory('Math')
    {
      'abi': [...],
      'bytecode': '0x...',
      'bytecode_runtime': '0x...',
      'metadata': {...},
    }


You may also want to retrieve all of the contract data for your project.  This
can be done with the :meth:`BaseChain.provider.get_all_contract_data` method.


.. code-block:: python

    >>> chain.provider.get_all_contract_data()
    {
      'Math': {'abi': [...], ...},
      'MyOtherContract': {'abi': [...], ...},
    }


Getting contract factories
--------------------------

The :meth:`BaseChain.provider.get_contract_factory` method gives you access to the
contract factory classes for your contracts.

.. code-block:: python

    >>> Math = chain.provider.get_contract_factory('Math')
    >>> Math.abi
    [...]
    >>> Math.bytecode
    "0x..."
    >>> Math.bytecode_runtime
    "0x..."

Contract factories returned by this method will be returned with their
underlying bytecode linked against the appropriate library addresses.  In the
event that one of the underlying dependencies is not available a
:class:`~populus.contracts.exceptions.NoKnownAddress` exception will be raised.

In some cases you may want the contract factory class without worrying about
whether the underlying bytecode linking.  Such contract factories are referred
to as *"base"* contract factories and can be retrieved using the
:meth:`BaseChain.provider.get_base_contract_factory` method.

.. code-block:: python

    >>> Math = chain.provider.get_base_contract_factory('Math')
    >>> Math.abi
    [...]
    >>> Math.bytecode
    "0x..."  # <-- may contain unlinked bytecode.
    >>> Math.bytecode_runtime
    "0x..."  # <-- may contain unlinked bytecode.


Registering contract addresses
------------------------------

When you deploy an instance of a contract populus stores the contract address
using the registry API.  This is an API that you should rarely need to interact
with directly as populus does the registration of new addresses automatically.
To set the address for a contract manually you would use the
:meth:`BaseChain.registrar.set_contract_address` method.

.. code-block:: python

    >>> chain.registrar.set_contract_address('Math', '0x...')


Retrieving contract addresses
-----------------------------

You can use the  :meth:`BaseChain.registrar.get_contract_addresses` method to
retrieve all known addresses for a given contract.  This method will return an
interable of addresses or throw a
`~populus.contracts.exceptions.NoKnownAddress` exception.


.. code-block:: python

    >>> chain.registrar.get_contract_address('Math')
    ['0x123abc....']


Retrieving contracts
--------------------

Populus provides the following APIs for retrieving instances of your deployed
contracts.

* :meth:`BaseChain.provider.get_contract`
* :meth:`BaseChain.provider.deploy_contract`
* :meth:`BaseChain.provider.get_or_deploy_contract`

The :meth:`BaseChain.provider.get_contract` function returns an instance of the
requested contract.


.. code-block:: python

    >>> math = chain.provider.get_contract('Math')
    >>> math.address
    '0x123abc....'

The :meth:`BaseChain.provider.deploy_contract` function will deploy a new
instance of the requested contract and return a two-tuple of the contract
instance and the transaction hash that it was deployed with.


.. code-block:: python

    >>> math, deploy_txn_hash = chain.provider.deploy_contract('Math')
    >>> math.address
    '0x123abc....'  # 20 byte hex encoded address
    >>> deploy_txn_hash
    '0xabcdef...'  # 32 byte hex encoded transaction hash



The :meth:`BaseChain.provider.get_or_deploy_contract` function is primarily for
testing purposes.  If the contract is already available this method will return
a two tuple of the contract instance and ``None``.  If the contract is not
available it will be deployed using the provided deploy transaction and
arguments, returning a two tuple of the contract instance and the deploy
transaction hash.


.. code-block:: python

    >>> math, deploy_txn_hash = chain.provider.get_or_deploy_contract('Math')
    >>> math.address
    '0x123abc....'  # 20 byte hex encoded address
    >>> deploy_txn_hash
    '0xabcdef...'  # 32 byte hex encoded transaction hash
    >>> chain.provider.get_or_deploy_contract('Math')
    (<Math at 0x123abc>, None)


Checking availability of contracts
----------------------------------

Sometimes it may be useful to query whether a certain contract or its
dependencies are available.  This can be done with the following APIs.

* :meth:`BaseChain.provider.are_contract_dependencies_available`
* :meth:`BaseChain.provider.is_contract_available`

The :meth:`BaseChain.provider.are_contract_dependencies_available` method
returns ``True`` if all of the necessary dependencies for the provided contract
are avialable.  This check includes checks that the bytecode for all
dependencies matched the expected compiled bytecode.

The :meth:`BaseChain.provider.is_contract_available` method returns ``True`` if
all dependencies for the requested contract are available **and** there is a
known address for the contract **and** the bytecode at the address matches the
expected bytecode for the contract.
