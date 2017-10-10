Part 4: Connecting to a `testrpc` Node
======================================

.. contents:: :local:


First, install `eth-testrpc`:

.. code-block:: bash

    $ pip install eth-testrpc

After installation, run:

.. code-block:: bash

    $ testrpc-py

    Available Accounts
    ==================
    0x82a978b3f5962a5b0957d9ee9eef472ee55b42f1
    0x7d577a597b2742b498cb5cf0c26cdcd726d39e6e
    0xdceceaf3fc5c0a63d195d69b1a90011b7b19650d
    0x598443f1880ef585b21f1d7585bd0577402861e5
    0x13cbb8d99c6c4e0f2728c7d72606e78a29c4e224
    0x77db2bebba79db42a978f896968f4afce746ea1f
    0x24143873e0e0815fdcbcffdbe09c979cbf9ad013
    0x10a1c1cb95c92ec31d3f22c66eef1d9f3f258c6b
    0xe0fc04fa2d34a66b779fd5cee748268032a146c0
    0x90f0b1ebbba1c1936aff7aaf20a7878ff9e04b6c

    Listening on localhost:8545

.. note:: Make sure that you are actually running python `testrpc`, not the javascript version.

Then add some new configs to `populus.json`:

.. code-block:: javascript

    {
      "chains": {

        ...

        "local": {
          "chain": {
            "class": "populus.chain.ExternalChain"
          },
          "contracts": {
            "backends": {
              "Memory": {
                "$ref": "contracts.backends.Memory"
              },
              "ProjectContracts": {
                "$ref": "contracts.backends.ProjectContracts"
              },
              "TestContracts": {
                "$ref": "contracts.backends.TestContracts"
              }
            }
          },
          "web3": {
            "$ref": "web3.Local"
          }
        }
      }

      ...

      "web3": {

        ...

        "Local": {
          "provider": {
            "class": "web3.providers.rpc.HTTPProvider",
            "settings": {
              "endpoint_uri": "http://localhost:8545"
            }
          }
        }
      }
    }

Now, deploy the contract to `testrpc` node:

.. code-block:: bash

    $ populus deploy --chain local --no-wait-for-sync Greeter

    > Found 1 contract source files
      - contracts/Greeter.sol
    > Compiled 1 contracts
      - contracts/Greeter.sol:Greeter
    Beginning contract deployment.  Deploying 1 total contracts (1 Specified, 0 because of library dependencies).

    Greeter
    Deploying Greeter
    Deploy Transaction Sent:
    0x7eddc9a2b6e866388de4a7f029fa39030d752d72cc9e602cfb71d4257bb8d1e8
    Waiting for confirmation...

    Transaction Mined
    =================
    Tx Hash      :
    0x7eddc9a2b6e866388de4a7f029fa39030d752d72cc9e602cfb71d4257bb8d1e8
    Address      : 0xc305c901078781c232a2a521c2af7980f8385ee9
    Gas Provided : 469607
    Gas Used     : 369607


    Verified contract bytecode @ 0xc305c901078781c232a2a521c2af7980f8385ee9
    Deployment Successful.

.. note:: The output address `0xc305c901078781c232a2a521c2af7980f8385ee9` will be used later to verify contract deployment.

And you should see these logs from `testrpc` node:

.. code-block:: bash

    127.0.0.1 - - [02/Sep/2017 14:55:06] "POST / HTTP/1.1" 200 48
    127.0.0.1 - - [02/Sep/2017 14:55:06] "POST / HTTP/1.1" 200 44
    127.0.0.1 - - [02/Sep/2017 14:55:06] "POST / HTTP/1.1" 200 2414
    127.0.0.1 - - [02/Sep/2017 14:55:06] "POST / HTTP/1.1" 200 107
    127.0.0.1 - - [02/Sep/2017 14:55:06] "POST / HTTP/1.1" 200 3071
    127.0.0.1 - - [02/Sep/2017 14:55:06] "POST / HTTP/1.1" 200 391
    127.0.0.1 - - [02/Sep/2017 14:55:06] "POST / HTTP/1.1" 200 391
    127.0.0.1 - - [02/Sep/2017 14:55:06] "POST / HTTP/1.1" 200 2163
    127.0.0.1 - - [02/Sep/2017 14:55:06] "POST / HTTP/1.1" 200 2164

Finally, use `web3.py` to check if the contract is successfully deployed. This is done by checking if the given contract address `0xc305c901078781c232a2a521c2af7980f8385ee9` has corresponding bytecode:


.. code-block:: bash

    $ pip install web3


.. code-block:: python

    >>> from web3 import Web3, HTTPProvider, IPCProvider
    >>> web3 = Web3(HTTPProvider('http://localhost:8545'))
    >>> web3.eth.getCode("0xc305c901078781c232a2a521c2af7980f8385ee9")

    u'0x60606040526000357c....

