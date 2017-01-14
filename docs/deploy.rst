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

    Deployment currently cannot handle contracts that require constructor arguments.


Deploying Your First Contract
-----------------------------

Deployment is handled through the ``$ populus deploy`` command.


.. code-block:: shell

	$ populus deploy --help
	Usage: populus deploy [OPTIONS] [CONTRACTS_TO_DEPLOY]...

      Deploys the specified contracts to a chain.

	Options:
	  -c, --chain TEXT        Specifies the chain that contracts should be
							  deployed to. The chains mainnet' and 'morden' are
							  pre-configured to connect to the public networks.
							  Other values should be predefined in your
							  populus.ini
	  -h, --help              Show this message and exit.<Paste>


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


We can deploy this contract to a local test chain like thi.

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
	Registering contract 'Wallet' @ 0xb6fac5cb309da4d984bb6145078104355ece96ca in registrar in txn: 0xca91ff346d63d9cec452ba94d8b2e650d8169b9b14fdf5ca76f770c1ce3a997f ... DONE
	Deployment Successful.


Above you can see the output for a basic deployment.
