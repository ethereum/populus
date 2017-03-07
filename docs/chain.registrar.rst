.. _chain-registrar:

Provider API
--------

.. module:: populus.contracts.registrar
.. currentmodule:: populus.contracts.registrar

.. py:class:: Registrar(chain, registrar_backends)


Each chain object exposes the following API through a property
:ref:`Chain.registrar <chain-api-registrar>`.  


.. py:method Registrar.set_contract_address(contract_name, address)

    Record the provided ``address`` in the registrar backends.


.. py:method Registrar.get_contract_addresses(contract_name)

    Returns a tuple of all known addresses for the provided ``contract_name``.
