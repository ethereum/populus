Part 4: Publishing a Package
============================

.. contents:: :local:


Introduction
------------

In the previous tutorial we explored installing packages and using the
contracts from those packages in our project.

This tutorial will pick up where that one left off.  We will be publishing our
``mintable-standard-token`` package to `The Package Registry`_.


Configuring Populus for Publishing
----------------------------------

In order to publish our package you will need to add some configuration to the
the ``RopstenPackageIndexBackend`` which can be found in the ``populus.json``
file in the root of the project.  It *should* currently look like this.

.. code-block:: javascript

    "RopstenPackageIndexBackend": {
      "class": "populus.packages.backends.index.PackageIndexBackend",
      "priority": 40,
      "settings": {
        "package_index_address": "0x8011df4830b4f696cd81393997e5371b93338878",
        "web3-for-install": {
          "$ref": "web3.InfuraRopsten"
        }
      }
    }


We're going to add the key ``web3-for-publish`` to the ``settings`` portion of
this config.  Populus will need to be able to send transactions through the
configured web3 instances.  For the purposes of this tutorial you will need to
run a ``geth`` node that is connected to the *Ropsten* testnetwork with an
unlocked account.  Modify the config to look like the following, but with your
address substituted in place the address
``0xaffa9e11a8deac514b93169c764aa042b4fe316f`` and the path to your
``geth.ipc`` file for the running ropsten instance.

.. code-block:: javascript

    "RopstenPackageIndexBackend": {
      "class": "populus.packages.backends.index.PackageIndexBackend",
      "priority": 40,
      "settings": {
        "package_index_address": "0x8011df4830b4f696cd81393997e5371b93338878",
        "web3-for-install": {
          "$ref": "web3.InfuraRopsten"
        },
        "web3-for-publish": {
          "provider": {
            "class": "web3.providers.ipc.IPCProvider",
            "settings": {
              "ipc_path": "/Users/piper/Library/Ethereum/ropsten/geth.ipc"
            }
          },
          "eth": {
            "default_account": "0xaffa9e11a8deac514b93169c764aa042b4fe316f"
          }
        }
      }
    }


Configuring your package for publishing
---------------------------------------

The next thing you'll need to do is rename your package to something other than
``mintable-standard-token`` as that package name is already registered on the
package index.  The package name is set in the ``ethpm.json`` file located in the
root of the project.


Building the release lockfile
-----------------------------

To build the package we will use the ``$ populus package build`` command.  We
want to include our ``MintableToken`` contract in the release.  Use the
following command to build the release lockfile.

.. code-block:: bash

    $ populus package build --contract-type MintableToken
    Wrote release lock file: build/1.0.0.json

If you open up the built release lockfile ``./build/1.0.0.json`` you should see something similar to the following (which was truncated for readability sake).

.. code-block:: javascript

    {
      "build_dependencies": {
        "example-package-owned": "ipfs://QmUwVUMVtkVctrLDeL12SoeCPUacELBU8nAxRtHUzvtjND",
        "example-package-standard-token": "ipfs://QmegJYswSDXUJbKWBuTj7AGBY15XceKxnF1o1Vo2VvVPLQ"
      },
      "contract_types": {
        "MintableToken": {
          "abi": [
            ..
          ],
          "bytecode": "0x60606040525b60....",
          "contract_name": "MintableToken",
          "natspec": {
            "methods": {
              "balanceOf(address)": {
                "details": "Returns number of tokens owned by given address.",
                "params": {
                  "_owner": "Address of token owner."
                }
              },
              ...
            }
          },
          "runtime_bytecode": "0x606060405236156..."
        }
      },
      "lockfile_version": "1",
      "meta": {
        "authors": [
          "Piper Merriam <pipermerriam@gmail.com>"
        ],
        "description": "Mintable ERC20 token contract",
        "keywords": [
          "ERC20",
          "tokens"
        ],
        "license": "MIT",
        "links": {}
      },
      "package_name": "mintable-standard-token",
      "sources": {
        "./contracts/MintableToken.sol": "ipfs://QmWUWwXdR6d5BycZYoDVyv4gkEEYkv9ixwQpLoePLNGPBE"
      },
      "version": "1.0.0"
    }


Publishing the release lockfile
-------------------------------

The last step is to publish the release lockfile.  This is done with the ``$
populus package publish`` command.

.. code-block:: bash

    $ populus package publish build/1.0.0.json
    Publishing to RopstenPackageIndexBackend


If you wait for the transaction to be confirmed and head over to `The Package
Registry`_ you should see your newly published package in the package index.

.. _The Package Registry: http://www.ethpm.com/
