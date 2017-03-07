.. _chain-provider:

Provider API
--------

.. module:: populus.contracts.provider
.. currentmodule:: populus.contracts.provider

.. py:class:: Provider(chain, provider_backends)


Each chain object exposes the following API through a property
:ref:`Chain.provider <chain-api-provider>`.  


.. py:method:: Provider.are_contract_dependencies_available(contract_identifier)

    Returns a boolean indicating whether all of the dependencies for the given
    contract are available.  All dependencies will have their on-chain bytecode
    checked against the expected compiler output.


.. py:method:: Provider.is_contract_available(contract_identifier)

    Returns a boolean indicating the contract is available through the Provider
    backend.  This checks all of the following.
    
    * There is a known address for the contract in the Registrar.
    * All of the dependencies for this contract are available.
    * The fully linked bytecode for this contract matches the bytecode found on-chain.
