Legacy Chain API
================

Previously, chain objects provided an API for accessing your contract compile
and deploy artifacts.  This API was moved to the :ref:`Provider API <chain-contracts>` 
in the :ref:`1.6.0 Release <v1.6.0-release-notes>`.

Access To Contracts
-------------------

All chain objects present the following API for interacting with your project
contracts.

.. warning:: 
    The ``Chain.get_contract_factory`` API has moved to the :ref:`Provider API
    <chain-provider>`.  This function will be removed in subsequent releases.

- ``get_contract_factory(contract_name, link_dependencies=None, validate_bytecode=True)``

    Returns the contract factory for the contract indicated by
    ``contract_name`` from the chain's ``compiled_contracts``.

    If provided, ``link_dependencies`` should be a dictionary that maps library
    names to their on chain addresses that will be used during bytecode
    linking.

    If truthy (the default), ``validate_bytecode`` indicates whether the
    bytecode for any library dependencies for the given contract should be
    validated to match the on chain bytecode.

    If your project has no project migrations then the data used for these
    contract factories will come directly from the compiled project contracts.

    If your project has migrations then the data used to build your contract
    factories will be populutated as follows.:

        #. The newest migration that has been run which deploys the requested
           contract.
        #. The newest migration which contains this contract in it's
           ``compiled_contracts`` property
        #. The compiled project contracts.


.. warning:: 
    The ``Chain.get_contract`` API has moved to the :ref:`Provider API
    <chain-provider>`.  This function will be removed in subsequent releases.

- ``get_contract(contract_name, link_dependencies=None, validate_bytecode=True)``

    Returns the contract instance indicated by the ``contract_name`` from the
    chain's ``compiled_contracts``.

    The ``link_dependencies`` argument behaves the same was as specified in the
    ``get_contract_factory`` method.

    The ``validate_bytecode`` argument behaves the same way as specified in the
    ``get_contract_factory`` with the added condition that the bytecode for the
    requested contract will also be checked.

    .. note::
        
        When using a ``TestRPCChain`` the ``get_contract`` method will lazily
        deploy your contracts for you.  This lazy deployment will only work for
        simple contracts which do not require constructor arguments.


.. warning:: 
    The ``Chain.is_contract_available`` API has moved to the :ref:`Provider API
    <chain-provider>`.  This function will be removed in subsequent releases.

- ``is_contract_available(contract_name, link_dependencies=None, validate_bytecode=True, raise_on_error=False)``

    Returns ``True`` or ``False`` as to whether the contract indicated by
    ``contract_name`` from the chain's ``compiled_contracts`` is available
    through the ``Chain.get_contract`` API.

    The ``link_dependencies`` argument behaves the same was as specified in the
    ``get_contract_factory`` method.

    The ``validate_bytecode`` argument behaves the same way as specified in the
    ``get_contract_factory`` with the added condition that the bytecode for the
    requested contract will also be checked.

    If ``raise_on_error`` is truthy, then the method will raise an exception
    instead of returning ``False`` for any of the failure cases.
