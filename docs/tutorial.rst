Getting started
---------------

.. contents:: :local:

Introduction
~~~~~~~~~~~~

The following is a quick introduction to a session using populus to
deploy a simple contract, run a test chain, and then make some
transaction and calls to that deployed contract.

Getting started
~~~~~~~~~~~~~~~

First create your project using :ref:`init`.

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
