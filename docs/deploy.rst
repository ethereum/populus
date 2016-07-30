Deploy
======

.. contents:: :local:

Introduction
------------

Deployment is a process where you take the contract ABI definition
and create a new smart contract in a blockchain with its own address
and balance.

Deploying contracts using a command line client
-----------------------------------------------

.. code-block:: shell

    $ populus deploy --help
    Usage: populus deploy [OPTIONS] [CONTRACTS_TO_DEPLOY]...

      Deploys the specified contracts via the RPC client.

    Options:
      -d, --dry-run                  Do a dry run deploy first.  When doing a
                                     production deploy, you should always do a dry
                                     run so that deploy gas prices can be known.
      -n, --dry-run-chain-name TEXT  Specifies the chain name that should be used
                                     for the dry run deployment.  Defaults to
                                     'default'
      -p, --production               Deploy to a production chain (RPC server must
                                     be run manually)
      --confirm / --no-confirm       Bypass any confirmation prompts
			--record / --no-record         Record the created contracts in the
			                               'known_contracts' lists. This only works for
																		 non-production chains.
      --help                         Show this message and exit.

Running ``$ populus deploy`` will deploy all specifed contracts to either the
default test chain or to a running JSON-RPC server depending on whether
``--production`` was specified.

If the ``--dry-run`` flag is specified, then the gas value supplied for each
contract's deployment will be determined based on how much gas was used during
the dry run deployment.

When using the ``--production`` flag populus will not run the JSON-RPC for you.
You are expected to have an RPC server running with an unlocked account.  Doing
a production deploy without ``--dry-run`` is not advisable.  Doing a dry run
ensures that all of your contracts are deployable as well as allowing the
production deployment to supply gas values determined from the dry run
deployments.

.. note::
    When using libraries, populus will try to link your libraries.  This
    functionality is experimental and could still have bugs.

Deploying contracts programmatically
------------------------------------

Below is an example how to use web3 to deploy a contract.

.. code-block:: python

    from typing import Optional, Tuple

    from web3 import Web3
    from web3.contract import _Contract, construct_contract_class

    from populus.utils.transactions import get_contract_address_from_txn


    def deploy_contract(
            web3: Web3,
            contract_definition: dict,
            gas=1500000,
            timeout=60.0,
            constructor_arguments: Optional[list]=None,
            from_account=None) -> Tuple[_Contract, str]:
        """Deploys a single contract using Web3 client.

        :param web3: Web3 client instance

        :param contract_definition: Dictionary of describing the contract interface,
            as read from ``contracts.json`` Contains

        :param gas: Max gas

        :param timeout: How many seconds to wait the transaction to
            confirm to get the contract address.

        :param constructor_arguments: Arguments passed to the smart contract
            constructor. Automatically encoded through ABI signature.

        :param from_account: Geth account that's balance is used for deployment.
            By default, the gas is spent from Web3 coinbase account. Account must be unlocked.

        :return: Tuple containing Contract proxy object and the transaction hash where it was deployed

        :raise gevent.timeout.Timeout: If we can't get our contract in a block within given timeout
        """

        # Check we are passed valid contract definition
        assert "abi" in contract_definition, \
            "Please pass a valid contract definition dictionary, got {}".format(contract_definition)

        contract_class = construct_contract_class(
            web3=web3,
            abi=contract_definition["abi"],
            code=contract_definition["code"],
            code_runtime=contract_definition["code_runtime"],
            source=contract_definition["source"],
                )

        if not from_account:
            from_account = web3.eth.coinbase

        # Set transaction parameters
        transaction = {
            "gas": gas,
            "from": from_account,
        }

        # Call web3 to deploy the contract
        txn_hash = contract_class.deploy(transaction, constructor_arguments)

        # Wait until we get confirmation and address
        address = get_contract_address_from_txn(web3, txn_hash, timeout=timeout)

        # Create Contract proxy object
        contract = contract_class(
            address=address,
            abi=contract_definition["abi"],
            code=contract_definition["code"],
            code_runtime=contract_definition["code_runtime"],
            source=contract_definition["source"])

        return contract, txn_hash


Funding deployed contract
-------------------------

Below is an example how to fund a deployed contract.
This is mainly aimed for testing.

.. code-block:: python

    def send_balance_to_contract(contract: Contract, value: Decimal) -> str:
        """Send balance from geth coinbase to the contract.

        :param contract: Contract instance with an address

        :param value: How much to send

        :return: Transaction hash of the send operation
        """
        web3 = contract.web3
        tx = {
            "from": web3.eth.coinbase,
            "to": contract.address,
            "value": to_wei(value)
        }
        return web3.eth.sendTransaction(tx)

