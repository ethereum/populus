Overview
========

Populus is a framework for developing applications for Ethereum.


Installation
------------

install ``populus``

.. code-block:: shell

   $ pip install populus

Populus has one dependency that cannot be bundled with the package until
upstream changes are merged into the respective repository.  You can install
this dependencies directly with the following commands.

.. code-block:: shell

    $ pip install https://github.com/ethereum/ethash/archive/v23.1.tar.gz

See https://github.com/ethereum/ethash/issues/72 for detailed information on the
upstream changes that these two direct installs address.


Project Layout
--------------

By default populus expects a project to be layed out as follows.

.. code-block:: shell

    ├── project root
    │   ├── build
    │   │   └── contracts.json
    │   ├── contracts
    │   |   ├── MyContract.sol
    |   |   ├── ....
    │   ├── libraries
    │   |   ├── MyLibrary.sol
    |   |   ├── ....
    │   ├── tests
    │   |   ├── test_my_contract.py
    │   |   ├── test_some_other_tests.py
    |   |   ├── ....
    │   ├── html
    │   │   └── index.html
    │   └── assets
    │       └── ....


Command Line Options
--------------------

.. code-block:: shell

    $ populus --help
    Usage: populus [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      attach   Enter a python shell with contracts and...
      chain    Wrapper around `geth`.
      compile  Compile project contracts, storing their...
      deploy   Deploy contracts.
			eventlog Produces a log of events that are generated...
      init     Generate project layout with an example...
      web      HTML/CSS/JS tooling.


Initialize
~~~~~~~~~~

Running ``$ populus init`` will initialize the current directory with the
default project layout that populus uses.

* ``./contracts/``
* ``./contracts/Example.sol``
* ``./tests/test_examply.py``
* ``./html/index.html``
* ``./assets/``


Attach
~~~~~~

Running ``$ populus attach`` with place you in an interactive python shell with
your contract classes and an RPC client available in the local namespace.


.. code-block:: shell

    $ populus attach
    Python: 2.7.10 (default, Jul 13 2015, 12:05:58)

    Populus: v0.5.2

    Project Path: /path/to/my-project/

    contracts  -> Contract classes
    client     -> Blockchain client (json-rpc)

    Contracts: Example, AnotherExample

    ... > 


Compile
~~~~~~~

Running ``$ populus compile`` will compile all of the contracts found in the
``./contracts/`` directory as well as all libraries found in the
``./libraries/`` directory.  The compiled projects are stored in
``./build/contracts.json``.

.. note::

    Currently, populus only supports import statemens for solidity files found
    in the ``./libraries/`` directory.  These should be in the format ``import
    "libraries/MyLibrary.sol";``.

Basic usage to compile all of the contracts and libraries in your project can
be done as follows.

.. code-block:: shell

    $ populus compile
    ============ Compiling ==============
    > Loading contracts from: /var/projects/my-project/contracts
    > Found 2 contract source files
    - mortal.sol
    - owned.sol

    > Compiled 3 contracts
    - Immortal
    - Mortal
    - owned

    > Outfile: /var/projects/my-project/build/contracts.json


If you only want to build a sub-set of your contracts you can specify paths to
source files, or the names of contracts in source files, or a combination of
the two separated by a ``:``.

* ``$ populus compile Example`` - compiles all contracts named Example.
* ``$ populus compile contracts/Example.sol`` - compiles all contracts in the
  specified file.
* ``$ populus compile contracts/Example.sol:Example`` - compiles all contracts
  named Example in in the specified file.


Additionally, you can pass in ``--watch`` to have Populus watch your contract
source files and automatically rebuild them when those files change.

.. code-block:: shell

    $ populus compile --watch
    ============ Compiling ==============
    > Loading contracts from: /var/projects/my-project/contracts
    > Found 2 contract source files
    - mortal.sol
    - owned.sol

    > Compiled 3 contracts
    - Immortal
    - Mortal
    - owned

    > Outfile: /var/projects/my-project/build/contracts.json
    ============ Watching ==============
    
    # Then you save a file....

    ============ Detected Change ==============
    > modified => /var/projects/my-project/contracts/mortal.sol
    > recompiling...
    > watching...


Output is serialized as ``JSON`` and written to ``build/contracts.json``
relative to the root of your project.

.. code-block:: javascript

    {
        "Example": {
            "code": "0x60606040525b5b600a8060136000396000f30060606040526008565b00",
            "info": {
                "abiDefinition": [
                    {
                        "inputs": [],
                        "type": "constructor"
                    }
                ],
                "compilerVersion": "0.9.73",
                "developerDoc": null,
                "language": "Solidity",
                "languageVersion": "0",
                "source": "contract Example {\n        function Example() {\n        }\n}\n",
                "userDoc": null
            }
        }
    }

.. note::

    Populus currently only supports compilation of Solidity contracts.


Deploy
~~~~~~

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


Chain
~~~~~

Populus provides a wrapper around ``geth`` to facilitate management of
ephemeral test chains.  These commands are accessed through ``$ populus chain``

The blockchains that populus manages for you are stored in ``./chains`` in the
projec root.  All ``chain`` commands will operate on the 'default' chain.  You
can specify alternate chains by adding a name to the end of the command.

Each blockchain will have one account generated for it.

* ``$ populus chain run`` - Run a geth node backed by the 'default' test chain.
* ``$ populus chain run test1`` - Run a geth node backed by the 'test1' test
  chain which will be stored at ``./chains/test1/`` relative to your project
  root.
* ``$ populus chain reset`` - Reset the 'default' chain (truncates the
  blockchain, preserves accounts)
* ``$ populus chain reset test01`` - Reset the 'test1' chain (truncates the
  blockchain, preserves accounts)

EventLog
~~~~~~~~

Populus provides a means of parsing out the logs that are generated by 
events in solidity contracts. This command allows the user to set filters
on the contract objects and optionally the specific events that the 
contract generates. 

.. code-block:: shell

    $> populus eventlog --help
    Usage: populus eventlog [OPTIONS]

    Produces a log of events that are generated by contracts.

    Options:
      -f, --filt TEXT         This parameter is used to filter for events from a
                              particular contract. The format is a key-value style
                              format. Valid Keys are the following: contract,
                              address, event. The 'contract' key is required. The
                              'address' and 'event' keys are optional. If the
                              address option is not provided, the eventlog will
                              check the active project chain to determine which
                              known contract objects exist and match the latest
                              compiled code. If the filter does not include any
                              event filters, then all the events for a particular
                              contract will be monitored. User can pass multiple
                              of these options or none. If no contract options are
                              passed, then the eventlog will listen to all known
                              contract objects in the active chain for the current
                              project. Please see the populus documentation for
                              more information.
      --spec <json-file>      This parameter can be used to tell the eventlog to
                              read contract specifications from a particular JSON
                              file. This option can be passed multiple times. This
                              option is useful for cases where the contract that
                              you will to eventlog is not in this populus project.
                              Must be a full path name.
      --period FLOAT          Sets the polling period for the event log monitor in
                              seconds. Default is 1.0 seconds.
      --active / --no-active  This flag indicates whether the attach command will
                              use the chain that is referenced from the
                              <proj>/chains/.active-chain to load information
                              about known contracts or not. Default is to load the
                              active chain if present.
      --rpc <IP>:<PORT>       Set the RPC endpoint to which we will listen for
                              events. Default: 127.0.0.1:8545
      -v, --verbose           Print more verbose information
      --help                  Show this message and exit.

Examples:
^^^^^^^^^
Below are just some quick examples to show whats possible 

.. code-block:: shell

    # Starting logging only the "MakeAnEvent" events from the
    #   Example Contract. 
    $> populus eventlog -f contract=Example,event=MakeAnEvent

    # Starting logging any events from Example Contract. 
    $> populus eventlog -f contract=Example

    # Starting logging any events from Example Contract with address
    $> populus eventlog -f contract=Example,address=0x12341231..1234



Filters
^^^^^^^

Filters consist of a comma-delimited string of key-value pairs. Currently,
the eventlog accepts the following keys: 

 - 'contract' - Allows the user to name a contract to listen for events from. This key-value pair argument in a filter string is required. The value must name one of the Contracts in this project. Alternatively, the user can supply an additional 'contracts.json' file via the '--spec' option to give move contract's to select from. 
 - 'address' - Allows the user to select a particular contract by address. This address may be in the current project or it could be on a chain somewhere else. This address must be in hexadecimal form. 
 - 'event' - Allows the user to filter for a particular event from the given contract. Multiple key-value pairs with this key can be used in a filter string. If this argument is not present, then all the events on a particular contract will be logged. 

Example Session
^^^^^^^^^^^^^^^

The following shows an example session. The contract 'Example' has 
two events: 

 - event MakeAnEvent(string msg); 
 - event MakeAnotherEvent(string msg, uint val); 

These events get generated when code in the contract runs as a transaction.
The event log picks up these events and prints them to the eventlog
terminal.

.. code-block:: shell

    $> populus eventlog -f contract=Example
    Event Logger Starting...
    {'data': {u'msg': 'Fishy Fishy Fishy'}, 'event': u'MakeAnEvent', 'contract': 'Example', 'address': u'0xb1103025982cbec4b3bb9c4e1944eec75ed6b0df'}
    {'data': {u'msg': 'This is some text', u'val': 1234}, 'event': u'MakeAnotherEvent', 'contract': 'Example', 'address': u'0xb1103025982cbec4b3bb9c4e1944eec75ed6b0df'}


Info about the keys in the generated json objects: 

- 'data' - Contains the arguments that were passed to the event when called in the transaction.
- 'event' - Name of the event that generated this log. 
- 'contract' - Name of the contract that generate this event. 
- 'address' - Address of the contract that generated this log. 


Web
~~~

Populus provides utilies for running a development webserver for DApp
development.  These commands are accessed via ``$ populus web``


Initialization
^^^^^^^^^^^^^^

You can initialize the html/css/js portions of your project with ``$populus web init``.

This will create ``html`` and ``assets`` directories in your project root. As
well as an ``./html/index.html`` document.


.. code-block:: shell
    ├── project root
    │   ├── html
    │   │   └── index.html
    │   └── assets
    │       └── ....


Runserver
^^^^^^^^^

Use ``$ populus web runserver`` to run the development server.

.. note:: This feature is extremely new and under active development.  Your contracts, while available as web3 contracts, are not automatically deployed.  Next steps in developing this will include running one of the test chains in the background and having your contracts auto-deployed to that chain.


Static assets
"""""""""""""

The development server is a simple flask application that serves your
``./html/index.html`` document as well as providing access to the static assets
in the ``./assets/`` directory.  All of the assets in that directory can be
accessed in your html document prefixed with the url ``/static/``.  For
example, the css file ``./assets/css/base.css`` would be accessible with the
url ``/static/css/base.css``.

The ``runserver`` command also watches for changes to your contracts and
assets, recompiling, or recollecting assets as necessary.

web3.js
"""""""

Populus includes a vendored version of ``web3.js``.  If you would like to
provide your own, simply place it at ``./assets/js/web3.js`` and your version
will be used instead.


javascript contracts
""""""""""""""""""""

All of your contracts are accessible via the ``contracts`` object which is
available in the global javascript scope.  This is provided by a generated
``js/contracts.js`` file.

.. warning:: if you place a file at ``./assets/js/contracts.js`` then you will have overridden the generated javascript file that provides access to your contracts.


Example Session
---------------

The following is a quick introduction to a session using populus to
deploy a simple contract, run a test chain, and then make some
transaction and calls to that deployed contract.

Modify 'Example.sol'
~~~~~~~~~~~~~~~~~~~~

We're going to add a couple of methods to make Example.sol a little
more interesting for this demo. It should look something like this:

.. code-block:: shell

    contract Example {
	      uint val;
	      function Example() {
		        val = 0;
	      }

	      function GetValue() constant returns(uint) {
		        return(val);
	      }

	      function Increment() {
		        val += 1;
	      }
    }

Notice that "GetValue" is a "constant" method and as such, will
map as a call and not a transaction. Increment modifies the state
of the contract, and as such, will make a transaction - not a call.

Workflow
~~~~~~~~

To get started, we will use the following commands to compile the
solidity contract and then to deploy it to our test chain.

.. code-block:: shell

    $ populus compile
    ============ Compiling ==============
    > Loading contracts from: /home/<user>/test3/contracts
    > Found 1 contract source files
    - Example.sol

    > Compiled 1 contracts
    - Example

    > Outfile: /home/<user>/test3/./build/contracts.json

    $ populus deploy -d
    ======= Executing Dry Run Deploy ========
    Chain Name     : default
    Data Directory : /home/<user>/test3/chains/default
    Geth Logfile   : /home/<user>/test3/chains/default/logs/deploy-dry-run-20151206-171821.log

    ... (deploying)

    ========== Deploy Completed ==========
    Deployed 1 contracts:
    - Example (0x78108355505f0fa551dbd1c97d1d102254532f83) gas: 149486 / 1092203143027

    ========== Executing Deploy ===========
    ... (deploying)
    Chain Name     : default
    Data Directory : /home/<user>/test3/chains/default
    Geth Logfile   : /home/<user>/test3/chains/default/logs/deploy-dry-run-20151206-171832.log

    ... (deploying)

    ========== Deploy Completed ==========
    Deployed 1 contracts:
    - Example (0xc0e0aa6088b4e9a9e4ef27123e3de9f499cf29ce) gas: 149486 / 164434


The deploy command's second run generates a new contract on the test
chain with address: "0xc0e0aa6088b4e9a9e4ef27123e3de9f499cf29ce". This
is the address that we will use for interacting with the contract.

Next, create a new terminal and run the following:

.. code-block:: shell

    $ populus chain run

    I1206 17:30:47.452321   39364 database.go:71] Alloted 16MB cache to /home/<user>/test3/chains/default/chaindata
    I1206 17:30:47.456924   39364 database.go:71] Alloted 16MB cache to /home/<user>/test3/chains/default/dapp
    I1206 17:30:47.458353   39364 backend.go:159] Protocol Versions: [63 62 61], Network Id: 123456
    I1206 17:30:47.458544   39364 statedb.go:265] (+) efd1aee872ec8e541cc81a1a99a4e806e4713de7
    I1206 17:30:47.458584   39364 state_object.go:184] efd1aee872ec8e541cc81a1a99a4e806e4713de7: #0 1000000000000000000000000000 (+ 1000000000000000000000000000)
    I1206 17:30:47.458810   39364 genesis.go:91] Genesis block already in chain. Writing canonical number
    I1206 17:30:47.458857   39364 backend.go:167] Successfully wrote custom genesis block: b659a9a050aba50f2a271d0a151ce05072700715fb3b02f8401b4f54ae62ef24
		...

This command will basically run indefinitely mining blocks. You can
kill it with Ctl-C like normal, but for now, let it run.

Now in our original terminal, we will use populus to attach a
console to the running chain.

.. code-block:: shell

    $ populus attach
    Python: 2.7.6 (default, Jun 22 2015, 17:58:13)

    Populus: v0.6.1

    Project Path: /home/<user>/test3

    contracts  -> Contract classes
    client     -> Blockchain client (json-rpc)
    redeploy   -> Method to redeploy project contracts
                  Example:
                    deployed_cts = redeploy()
                    deployed_cts = redeploy(record=False)
                    deployed_cts = redeploy(contracts = ["Example"])

    Contracts: Example
    Check contracts.<type>.known for deployed contracts.
    In [1]: exp = contracts.Example("0xc0e0aa6088b4e9a9e4ef27123e3de9f499cf29ce", client)

    In [2]: exp.GetValue()
    Out[2]: 0

    In [3]: txHash = exp.Increment()
		...
    In [5]: client.get_transaction_by_hash(txHash)
    Out[5]:
    {u'blockHash': u'0x478c1904aba3da5a0b78690cb68fd6229e5e7a2ca3a231a541a1a7672587467f',
      u'blockNumber': u'0x498',
      u'from': u'0xefd1aee872ec8e541cc81a1a99a4e806e4713de7',
      u'gas': u'0xe13f5e6f67',
      u'gasPrice': u'0xba43b7400',
      u'hash': u'0x8c645851b2edb197f5281aeb37a92a791d6892254bb745a813128fa94f3e9f23',
      u'input': u'0x648b7ce8',
      u'nonce': u'0xf',
      u'to': u'0xc0e0aa6088b4e9a9e4ef27123e3de9f499cf29ce',
      u'transactionIndex': u'0x0',
      u'value': u'0x0'}

    In [6]: exp.GetValue()
    Out[6]: 1

Items of note from above:

* "contracts" is an object that keeps our collection of contract object classes. Currently, there is only one 'Example', but you could have others as well.
* "client" is an rpc client with some methods that are useful for interrogating the chain and determine transaction information. Try running 'dir(client)' to get a list of some methods you can use.
* We create a new "Example" contract by feeding it the address that was generated by the deploy command and the rpc client object. 
* The 'exp.GetValue()' method is a call - so there is no transaction hash generated for this invokation. We just get the current state of the 'val' variable in the Example contract instance back immediately. 
* The 'exp.Increment()' method is a transaction. This call returns a hash that can be thought of as a reference to a transaction. Note that transactions are not processed immediately. They must be submitted to the ethereum test chain where they are pending transactions until they are processed into a block. 
* Finally, we call the "GetValue" method again and see that the value has been incremented as expected. 

Transactions that have not been processed yet look like the following. Notice that the "blockHash" and "blockNumber" value have not been populated yet.

.. code-block:: shell

    In [7]: txHash = exp.Increment()

    In [8]: client.get_transaction_by_hash(txHash)
    Out[8]:
    {u'blockHash': None,
      u'blockNumber': None,
      u'from': u'0xefd1aee872ec8e541cc81a1a99a4e806e4713de7',
      u'gas': u'0xe05e737ae3',
      u'gasPrice': u'0xba43b7400',
      u'hash': u'0x36546e13816b3bbd1492c07c12a7718dc820ce58c36648531c37fa7a8ee3ebc2',
      u'input': u'0x648b7ce8',
      u'nonce': u'0x10',
      u'to': u'0xc0e0aa6088b4e9a9e4ef27123e3de9f499cf29ce',
      u'transactionIndex': None,
      u'value': u'0x0'}
		...
    In [12]: client.get_transaction_by_hash(txHash)
    Out[12]:
    {u'blockHash': u'0xffd83aeac5363d40849ab8b779cf07ea054e18cd01b36d38ba9f7a4a571ccc8b',
      u'blockNumber': u'0x49c',
      u'from': u'0xefd1aee872ec8e541cc81a1a99a4e806e4713de7',
      u'gas': u'0xe05e737ae3',
      u'gasPrice': u'0xba43b7400',
      u'hash': u'0x36546e13816b3bbd1492c07c12a7718dc820ce58c36648531c37fa7a8ee3ebc2',
      u'input': u'0x648b7ce8',
      u'nonce': u'0x10',
      u'to': u'0xc0e0aa6088b4e9a9e4ef27123e3de9f499cf29ce',
      u'transactionIndex': u'0x0',
      u'value': u'0x0'}

     In [13]: client.get_transaction_receipt(txHash)
     Out[13]:
     {u'blockHash': u'0xffd83aeac5363d40849ab8b779cf07ea054e18cd01b36d38ba9f7a4a571ccc8b',
       u'blockNumber': u'0x49c',
       u'contractAddress': None,
       u'cumulativeGasUsed': u'0x6781',
       u'gasUsed': u'0x6781',
       u'logs': [],
       u'transactionHash': u'0x36546e13816b3bbd1492c07c12a7718dc820ce58c36648531c37fa7a8ee3ebc2',
       u'transactionIndex': u'0x0'}

You can use the 'client.wait_for_transaction' method to block for a particular transaction to complete:

.. code-block:: shell

    In [15]: client.wait_for_transaction(txHash)
    Out[15]:
    {u'blockHash': u'0xffd83aeac5363d40849ab8b779cf07ea054e18cd01b36d38ba9f7a4a571ccc8b',
       u'blockNumber': u'0x49c',
       u'contractAddress': None,
       u'cumulativeGasUsed': u'0x6781',
       u'gasUsed': u'0x6781',
       u'logs': [],
       u'transactionHash': u'0x36546e13816b3bbd1492c07c12a7718dc820ce58c36648531c37fa7a8ee3ebc2',
       u'transactionIndex': u'0x0'}

Known Contracts
~~~~~~~~~~~~~~~

To make life a little easier, populus attempts to keep track of all of the known contracts in a particular ethereum test chain. This data is stored in the file "<proj>/chains/default/known_contracts.json". This file tracks the address of all deployed contracts and also stores a hash of the code of that contract when it was deployed. This allows the attach terminal to only show you the known contract instances that match your current compiled contract code. 

To look at the known contract instances in a particular test chain for a contract named "Example", you could look at the 'contracts.Example.known' member variable in the attach interpreter shell.

.. code-block:: shell

		In [1]: contracts.Example.known
		Out[1]:
		[<populus.contracts.core.Example at 0x7f45..90>,
		 <populus.contracts.core.Example at 0x7f45..10>]

		In [2]: contracts.example.known[0].GetValue() 
		Out[2]: 1

Redeploying Contracts
~~~~~~~~~~~~~~~~~~~~~

Sometimes it is useful to redeploy contracts while testing without 
exiting the attach shell. To help with this, there is the 'redeploy' 
method. The redeploy method is very similar to the "populus deploy"
command with some minor differences. This command will only deploy 
to the active test chain that this attach shell is talking to. The 
redeploy method will also not attempt to dry-run the contracts. 
The redeploy method will block waiting for all of the contract 
creation transactions to complete and receive their receipts.

.. code-block:: shell

		In[1]: depcts = redeploy() 
		========== Deploy Complete ==========
		Deployed 2 contracts: 
		- Example 2 (0x55157...67) gas: 216906 / 49829864
		- Example (0xd977...2a) gas: 162170 / 49732590
		
		In[2]: contracts.Example.known[-1].GetValue() 
		Out[2]: 0


The user can use the "populus compile" routine outside of the attach
shell to make modifications to project contracts and then use "redeploy" 
to quickly test these changes on a new contract instance. 

Note that the newly created contracts are added to the 'known' list. If 
the contract's binary changed by recompiling with changes, then the list 
will now have only one element. 

The 'redeploy' method takes two optional arguments: 

*  'record' - Boolean value indicating whether the created contract
   instances should be stored in the "known_contracts.json" 
   file. The default is True
*  'contracts' - List of strings indicating the names of the contracts 
   to redeploy. This is useful for only deploying a subset of the
   projects contracts. The default value is [] which means redeploy 
   all contracts. 

Changing Active Chains
~~~~~~~~~~~~~~~~~~~~~~

When you run an attach shell, you will generally want to run the "populus chain run" command first. This sets up the active chain directory before opening the shell. Additionally, you can change which chain is running during a attach shell session by killing the running chain and start a different one in the same project. For example: 

Let's say you start with the default test chain in Terminal #1

.. code-block:: shell

    $> populus chain run

    I1206 17:30:47.452321   39364 database.go:71] Alloted 16MB cache to /home/<user>/test3/chains/default/chaindata
    I1206 17:30:47.456924   39364 database.go:71] Alloted 16MB cache to /home/<user>/test3/chains/default/dapp
    I1206 17:30:47.458353   39364 backend.go:159] Protocol Versions: [63 62 61], Network Id: 123456

You then start up the attach shell

.. code-block:: shell

    $> populus attach

    Python: 2.7.6 (default, Jun 22 2015, 17:58:13)

    Populus: v0.6.1

    Project Path: /home/<user>/test3

    contracts  -> Contract classes
    client     -> Blockchain client (json-rpc)
    redeploy   -> Method to redeploy project contracts
                  Example:
                    deployed_cts = redeploy()
                    deployed_cts = redeploy(record=False)
                    deployed_cts = redeploy(contracts = ["Example"])

    Contracts: Example
    Check contracts.<type>.known for deployed contracts.
    In[1]: contracts.Example.known[0].GetValue()
    Out[1]: 0

Now Let's say you want to change over to another test chain to try something without mucking up your default chain state.

.. code-block:: shell

    $> populus chain run newtest

    I1206 17:30:47.452321   39364 database.go:71] Alloted 16MB cache to /home/<user>/test3/chains/newtest/chaindata
    I1206 17:30:47.456924   39364 database.go:71] Alloted 16MB cache to /home/<user>/test3/chains/newtest/dapp
    I1206 17:30:47.458353   39364 backend.go:159] Protocol Versions: [63 62 61], Network Id: 123456


The attach shell will watch for changes to the active test chain and reinitialize the known contract instances. 

.. code-block:: shell

		In[1]: contracts.Example.known[0].GetValue()
		Out[1]: 0

		In[2]:
		=========== Active Directory Changed ===========
		New Active Dir: /home/<user>/test3/chains/newtest

		In[2]: contracts.example.known
		Out[2]: []

The 'known' list is empty because no contracts have been deployed on this 
new test chain. 
