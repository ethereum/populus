Contracts
=========

Populus provides a python API for interacting with contracts.


``populus.contracts.Contract(rpc_client, contract_name, contract_abi):``
------------------------------------------------------------------------

This class-factory produces a class for your contract.  In addition to the
properties below, the contract will have `~populus.contracts.Function`
instances for each ``public`` function this contract exposes.

.. code-block:: python

    >>> math
    ... <populus.contracts.Math object at 0x106db1950>
    >>> math.address
    ... u'0xc305c901078781c232a2a521c2af7980f8385ee9'
    >>> math.client
    <populus.client.Client object at 0x106c13250>
    >>> math.code
    ... '0x606060405260f8806100126000396000f30060606040526000357c01000000000000000000000000000000000000000000000000000000009004806316216f3914604b578063a5f3c23b14606a578063dcf537b1146095576049565b005b605460045060e6565b6040518082815260200191505060405180910390f35b607f60048035906020018035906020015060ba565b6040518082815260200191505060405180910390f35b60a460048035906020015060d0565b6040518082815260200191505060405180910390f35b60008183019050805080905060ca565b92915050565b6000600782029050805080905060e1565b919050565b6000600d9050805080905060f5565b9056'
    >>> math.source
    ... 'contract Math {\n        function add(int a, int b) public returns (int result){\n            result = a + b;\n            return result;\n        }\n\n        function multiply7(int a) public returns (int result){\n            result = a * 7;\n            return result;\n        }\n\n        function return13() public returns (int result) {\n            result = 13;\n            return result;\n        }\n}\n'

``ContractClass(address)``
~~~~~~~~~~~~~~~~~~~~~~~~~~

Instantiate an instance of your contract with the ``hex`` encoded address of
where it is deployed.


``ContractClass.deploy(_from=None, gas=None, gas_price=None, value=None, args=None)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``classmethod`` for deploying the contract. Returns the transaction hash.  If
the contract constructor takes arguments, they should be passed in as the
``constructor_args`` argument.


``ContractClass.code``
~~~~~~~~~~~~~~~~~~~~~~

The compiled contract code.


``ContractClass.source``
~~~~~~~~~~~~~~~~~~~~~~

The contract source code.


``ContractClass.client``
~~~~~~~~~~~~~~~~~~~~~~~~

The JSON RPC client this contract will use.


``ContractClass.abi``
~~~~~~~~~~~~~~~~~~~~~

The contract ABI.


``ContractClass.get_balance(block="latest")``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns contract balance in wei as an integer.


``populus.contracts.Function(name, inputs, outputs=None, constant=False):``
---------------------------------------------------------------------------

Each contract will have a ``Funcion`` instance available for each of the
``public`` functions it provides.

.. code-block:: python

    >>> math
    ... <populus.contracts.Math object at 0x106db1950>
    >>> math.return13
    ... <populus.contracts.BoundFunction object at 0x1091b8190>
    >>> math.return13.sendTransaction(_from=eth_coinbase)
    ... u'0xe3362ce30b39be0499b8676bb54f8e773fae8b4425c7b9ad4c636a8c06fdf1be'
    >>> math.return13.call(_from=eth_coinbase)
    ... 13


``Function.sendTransaction(*args, _from=None, gas=None, gas_price=None, value=None)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Call the function by sending a transaction.  This returns the transaction hash.
This is aliased to simply calling the ``Function`` instance on the contract.

.. code-block:: python

    >>> math
    ... <populus.contracts.Math object at 0x106db1950>
    >>> math.return13.sendTransaction(_from=eth_coinbase)
    ... u'0xe3362ce30b39be0499b8676bb54f8e773fae8b4425c7b9ad4c636a8c06fdf1be'
    >>> math.return13(_from=eth_coinbase)  # Same as `math.return13.sendTransaction`
    ... u'0xe3362ce30b39be0499b8676bb54f8e773fae8b4425c7b9ad4c636a8c06fdf1be'


``Function.call(*args, _from=None, gas=None, gas_price=None, value=None)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Call the function and get the typed return value.  Does not send a transaction.

.. code-block:: python

    >>> math
    ... <populus.contracts.Math object at 0x106db1950>
    >>> math.return13.call(_from=eth_coinbase)
    ... 13

.. note::

    This may have undefined behavior if the function modifies the blockchain.
