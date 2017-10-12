Part 3: Deploy to a Local Chain
===============================

.. contents:: :local:


At part 2 of the tutorial you created a local chain named 'horton'. Now, we will deploy
the Greeter contract to this chain.


Project Config
--------------

First, we have to add the chain to the project configuration file:

.. code-block:: bash

  $ nano project.json


After edit, the project file should look like this:

.. code-block:: javascript

  {
    "version":"7",
    "compilation":{
      "contracts_source_dirs": ["./contracts"],
      "import_remappings": []
    },
    "chains": {
      "horton": {
        "chain": {
          "class": "populus.chain.ExternalChain"
        },
        "web3": {
          "provider": {
            "class": "web3.providers.ipc.IPCProvider",
          "settings": {
            "ipc_path":"/home/mary/projects/myproject/chains/horton/chain_data/geth.ipc"
          }
         }
        },
        "contracts": {
          "backends": {
            "JSONFile": {"$ref": "contracts.backends.JSONFile"},
            "ProjectContracts": {
              "$ref": "contracts.backends.ProjectContracts"
            }
          }
        }
      }
    }
  }



The ``ipc_path`` should be the exact ipc_path on your machine. If you are not sure,
copy-paste the path from the ``run_chain.sh`` script in the ``chains/horton/`` directory.


.. note::

  Populus uses JSON schema configuration files, on purpose. We think that for blockchain development, it's safer to
  use static, external configuration, than a Python module. For more about JSON
  based configuration see `JSON Schema <http://json-schema.org/>`_.

Note the line ``{"$ref": "contracts.backends.JSONFile"}``. There is a ``$ref``, but the reference
key does not exist in the file. This is beacuase the ``project.json`` config file is *complementary*
to the main populus user-scope config file, at ``~/.populus/config.json``. The user config holds
for all your populus projects, and you can use the ``project.json`` just for the configuration changes
that you need for a specific project. Thus, you can ``$ref`` the user-config keys in any project configuration file.




Running the Chain
-----------------

If the horton chain is not running (see part 2), run it. From the project directory, in another terminal,
use the script that Populus created:

.. code-block:: bash

  $ chains/horton/./run_chain.sh

You should see a ton of things that geth outputs.


Deploy
------

Finally, deploy the contract:

.. code-block:: bash

  $ deploy --chain horton Greeter --no-wait-for-sync

  > Found 1 contract source files
    - contracts/Greeter.sol
  > Compiled 1 contracts
    - contracts/Greeter.sol:Greeter
  Beginning contract deployment.  Deploying 1 total contracts (1 Specified, 0 because of library dependencies).

  Greeter

  Deploy Transaction Sent: 0x364d8d4b7e40992bed2ea5f92af833d58ef1b9f3b4171c1f64f8843c2527437d
  Waiting for confirmation...

After a few seconds the transaction is mined in your local chain:

.. code-block:: bash

  Transaction Mined
  =================
  Tx Hash      : 0x364d8d4b7e40992bed2ea5f92af833d58ef1b9f3b4171c1f64f8843c2527437d
  Address      : 0x1c51ff8a84345f0a5940601b3bd372d8105f71aa
  Gas Provided : 465580
  Gas Used     : 365579


  Verified contract bytecode @ 0x1c51ff8a84345f0a5940601b3bd372d8105f71aa
  Deployment Successful.


Well done!

.. note::

  We used here ``--no-wait-for-sync``, since the account has (a lot of) Eth from the get go, allocated
  in the genesis block. However, if you work with testnet or mainnet, you must sync at least until the block
  with the transactions that sent some Eth to the account you are deploying from. Otherwise, your local geth will not know
  that there is Eth in the account to pay for the gas. Once the chain is synced, you can deploy immidiatly.

