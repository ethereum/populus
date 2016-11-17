Part 3: Installing a Package
============================

.. contents:: :local:


Introduction
------------

In this tutorial we will be creating our own mintable `ERC20`_ token.  However,
instead of writing our own ERC20 implementation we'll be taking advantage of an
existing implementation through the use of populus's package management
features.


Setting up the project folder
-----------------------------


Create a new directory for your project and run ``$ populus project init`` to
populate the initial project structure.

.. code-block:: bash

    $ populus init
    Wrote default populus configuration to `./populus.json`.<Paste>
    Created Directory: ./contracts
    Created Example Contract: ./contracts/Greeter.sol
    Created Directory: ./tests
    Created Example Tests: ./tests/test_greeter.py

Now, delete the ``./contracts/Greeter.sol`` and ``./tests/test_greeter.py``
files as we won't be using the *Greeter* contracts in this tutorial.

Once you've removed those files create a new solidity source file
``./contracts/MintableToken.sol`` and paste in the following solidity source
code.

.. code-block:: solidity

    pragma solidity ^0.4.0;

    import {owned} from "example-package-owned/contracts/owned.sol";
    import {StandardToken} from "example-package-standard-token/contracts/StandardToken.sol";

    contract MintableToken is StandardToken(0), owned {
      function mint(address who, uint value) public onlyowner returns (bool) {
        balances[who] += value;
        totalSupply += value;
        Transfer(0x0, who, value);
        return true;
      }
    }

If you are familiar with solidity, the two import statements should stand out
to you.  These two statements will currently cause an error during compilation.
Let's see.

.. code-block:: bash

	$ populus compile
	============ Compiling ==============
	> Loading source files from: ./contracts

	Traceback (most recent call last):
	  ...
			> command: `solc --optimize --combined-json bin,bin-runtime,abi,devdoc,userdoc contracts/MintableToken.sol`
			> return code: `1`
			> stderr:

			> stdout:
			contracts/MintableToken.sol:3:1: Error: Source "example-package-owned/contracts/owned.sol" not found: File not found.
	import {owned} from "example-package-owned/contracts/owned.sol";
	^--------------------------------------------------------------^
	contracts/MintableToken.sol:4:1: Error: Source "example-package-standard-token/contracts/StandardToken.sol" not found: File not found.
	import {StandardToken} from "example-package-standard-token/contracts/StandardToken.sol";
	^---------------------------------------------------------------------------------------^

The solidity compiler clearly gets angry that we're trying to import files that
don't exist.  In order to install these file and make solidity happy we'll
first need to generate a package manifest using the ``$ populus package init``
command.

.. code-block::

	$ populus package init
	Writing new ethpm.json file.
	Package Name: mintable-standard-token
	Author(s) [[]]: Piper Merriam <pipermerriam@gmail.com>
	Version [1.0.0]:
	License [MIT]:
	Description []: Mintable ERC20 token contract
	Keywords [[]]: ERC20, tokens
	Links [{}]:
	Wrote package manifest: ethpm.json

You will be presented with an interactive prompt to populus various pieces of
project information.  There will now be a new file in the root of your project
named ``ethpm.json`` that should look something like this.

.. code-block:: javascript

	{
	  "authors": [
		"Piper Merriam <pipermerriam@gmail.com>"
	  ],
	  "description": "Mintable ERC20 token contract",
	  "keywords": [
		"ERC20",
		"tokens"
	  ],
	  "license": "MIT",
	  "links": {},
	  "manifest_version": "1",
	  "package_name": "mintable-standard-token",
	  "version": "1.0.0"
	}

Now we are ready to install some dependencies using the ``$ populus package
install`` command.  We want to install both the ``example-package-owned`` and
``example-package-standard-token`` packages.

.. code-block:: bash

    $ populus package install example-package-owned example-package-standard-token
    Installed Packages: owned, standard-token

If you look in your project directory you should also see a new folder
``./installed_packages``.

.. code-block:: bash

    $ tree .
    .
    ├── contracts
    │   └── MintableToken.sol
    ├── ethpm.json
    ├── installed_packages
    │   ├── example-package-owned
    │   │   ├── build_identifier.lock
    │   │   ├── contracts
    │   │   │   └── owned.sol
    │   │   ├── install_identifier.lock
    │   │   ├── installed_packages
    │   │   └── lock.json
    │   └── example-package-standard-token
    │       ├── build_identifier.lock
    │       ├── contracts
    │       │   ├── AbstractToken.sol
    │       │   └── StandardToken.sol
    │       ├── install_identifier.lock
    │       ├── installed_packages
    │       └── lock.json
    ├── populus.json
    └── tests

    9 directories, 12 files


And if you look in your ``ethpm.json`` file you should see two dependencies.


.. code-block:: javascript

    {
      "authors": [
        "Piper Merriam <pipermerriam@gmail.com>"
      ],
      "dependencies": {
        "example-package-owned": "1.0.0",
        "example-package-standard-token": "1.0.0"
      },
      "description": "Mintable ERC20 token contract",
      "keywords": [
        "ERC20",
        "tokens"
      ],
      "license": "MIT",
      "links": {},
      "manifest_version": "1",
      "package_name": "mintable-token",
      "version": "1.0.0"
    }

Now, we can try to compile our project again and everything should work.


.. code-block:: bash

    $ populus compile
    ============ Compiling ==============
    > Loading source files from: ./contracts

    > Found 1 contract source files
    - contracts/MintableToken.sol

    > Compiled 4 contracts
    - MintableToken
    - StandardToken
    - Token
    - owned

    > Wrote compiled assets to: ./build/contracts.json/contracts.json

Lets go ahead and write a quick test for our new minting functionality.  Add
the following test code to a new file ``./tests/test_token_minting.py``

.. code-block:: python

    import pytest

    def test_minting_tokens(chain, accounts):
        provider = chain.provider
        mintable_token, deploy_txn_hash = provider.get_or_deploy_contract(
            'MintableToken',
            deploy_kwargs={"_totalSupply": 0},
        )

        assert mintable_token.call().balanceOf(accounts[0]) == 0
        assert mintable_token.call().balanceOf(accounts[1]) == 0
        assert mintable_token.call().totalSupply() == 0

        chain.wait.for_receipt(mintable_token.transact().mint(
            who=accounts[0],
            value=12345,
        ))
        chain.wait.for_receipt(mintable_token.transact().mint(
            who=accounts[1],
            value=54321,
        ))

        assert mintable_token.call().balanceOf(accounts[0]) == 12345
        assert mintable_token.call().balanceOf(accounts[1]) == 54321
        assert mintable_token.call().totalSupply() == 66666

    def test_only_owner_can_mint(chain, accounts):
        provider = chain.provider
        mintable_token, deploy_txn_hash = provider.get_or_deploy_contract(
            'MintableToken',
            deploy_kwargs={"_totalSupply": 0},
        )

        with pytest.raises(Exception):
            mintable_token.transact({'from': accounts[1]}).mint(
                who=accounts[0],
                value=12345,
            )


And you can the tests with the ``py.test`` command.

.. code-block:: bash

    $ py.test tests/
    ========================= test session starts ========================
    platform darwin -- Python 3.5.2, pytest-3.0.4, py-1.4.31, pluggy-0.4.0
    rootdir: /Users/piper/sites/scratch/populus-tutorial-3, inifile:
    plugins: populus-1.5.0
    collected 2 items

    tests/test_token_minting.py ..

    ======================= 2 passed in 0.74 seconds =====================


Fin.


.. _ERC20: https://github.com/ethereum/EIPs/issues/20
