Deploy
======

.. contents:: :local:

Introduction
------------

The deployment functionality exposed by Populus is meant for one-off
deployments of simple contracts.  The deployment process includes some, or all
of the following steps.

#. Selection of which chain should be deployed to.
#. Running the given chain.
#. Compilation of project contracts.
#. Derivation of library dependencies.
#. Library linking.
#. Individual contract deployment.

.. note::

    The command line deployment command cannot be used to deploy contracts which require constructor arguments.


Deploying A Contract
--------------------

Deployment is handled through the ``$ populus deploy`` command.


Lets deploy a simple Wallet contract.  First we'll need a contract in our
project ``./contracts`` directory.

.. code-block:: solidity

	// ./contracts/Wallet.sol
	contract Wallet {
		mapping (address => uint) public balanceOf;

		function deposit() {
			balanceOf[msg.sender] += 1;
		}

		function withdraw(uint value) {
			if (balanceOf[msg.sender] < value) throw;
			balanceOf[msg.sender] -= value;
			if (!msg.sender.call.value(value)()) throw;
		}
	}


We can deploy this contract to a local test chain like this.

.. code-block:: shell

	$ populus deploy Wallet -c local_a
	Beginning contract deployment.  Deploying 1 total contracts (1 Specified, 0 because of library dependencies).

	Wallet
	Deploying Wallet
	Deploy Transaction Sent: 0x29e90f07314db495989f03ca931088e1feb7fb0fc13286c1724f11b2d6b239e7
	Waiting for confirmation...

	Transaction Mined
	=================
	Tx Hash      : 0x29e90f07314db495989f03ca931088e1feb7fb0fc13286c1724f11b2d6b239e7
	Address      : 0xb6fac5cb309da4d984bb6145078104355ece96ca
	Gas Provided : 267699
	Gas Used     : 167699


	Verifying deployed bytecode...
	Verified contract bytecode @ 0xb6fac5cb309da4d984bb6145078104355ece96ca matches expected runtime bytecode
    Deployment Successful.


Above you can see the output for a basic deployment.

Programmatically deploy a contract
----------------------------------

You can also deploy contracts using a Python script. This is a suitable method if your contracts need more complex initialization calls.

Example (``deploy_testnet.py``):

.. code-block:: python

    """Deploy Edgeless token and smart contract in testnet.

    A simple Python script to deploy contracts and then do a smoke test for them.
    """
    from populus import Project
    from populus.utils.cli import get_unlocked_default_account_address
    from populus.utils.wait import wait_for_transaction_receipt
    from web3 import Web3


    def check_succesful_tx(web3: Web3, txid: str, timeout=180) -> dict:
        """See if transaction went through (Solidity code did not throw).

        :return: Transaction receipt
        """

        # http://ethereum.stackexchange.com/q/6007/620
        receipt = wait_for_transaction_receipt(web3, txid, timeout=timeout)
        txinfo = web3.eth.getTransaction(txid)

        # EVM has only one error mode and it's consume all gas
        assert txinfo["gas"] != receipt["gasUsed"]
        return receipt


    def main():

        project = Project()

        # This is configured in populus.json
        # We are working on a testnet
        chain_name = "ropsten"
        print("Make sure {} chain is running, you can connect to it, or you'll get timeout".format(chain_name))

        with project.get_chain(chain_name) as chain:

            # Load Populus contract proxy classes
            Crowdsale = chain.get_contract_factory('Crowdsale')
            Token = chain.get_contract_factory('EdgelessToken')

            web3 = chain.web3
            print("Web3 provider is", web3.currentProvider)

            # The address who will be the owner of the contracts
            beneficiary = web3.eth.coinbase
            assert beneficiary, "Make sure your node has coinbase account created"

            # Random address on Ropsten testnet
            multisig_address = "0x83917f644df1319a6ae792bb244333332e65fff8"

            # Goes through coinbase account unlock process if needed
            get_unlocked_default_account_address(chain)

            # Deploy crowdsale, open since 1970
            txhash = Crowdsale.deploy(transaction={"from": beneficiary}, args=[beneficiary, multisig_address, 1])
            print("Deploying crowdsale, tx hash is", txhash)
            receipt = check_succesful_tx(web3, txhash)
            crowdsale_address = receipt["contractAddress"]
            print("Crowdsale contract address is", crowdsale_address)

            # Deploy token
            txhash = Token.deploy(transaction={"from": beneficiary}, args=[beneficiary])
            print("Deploying token, tx hash is", txhash)
            receipt = check_succesful_tx(web3, txhash)
            token_address = receipt["contractAddress"]
            print("Token contract address is", token_address)

            # Make contracts aware of each other
            print("Initializing contracts")
            crowdsale = Crowdsale(address=crowdsale_address)
            token = Token(address=token_address)
            txhash = crowdsale.transact({"from": beneficiary}).setToken(token_address)
            check_succesful_tx(web3, txhash)

            # Do some contract reads to see everything looks ok
            print("Token total supply is", token.call().totalSupply())
            print("Crowdsale max goal is", crowdsale.call().maxGoal())

            print("All done! Enjoy your decentralized future.")


    if __name__ == "__main__":
        main()


`See full source code repository example <https://github.com/miohtama/Edgeless-Smart-Contracts>`_.