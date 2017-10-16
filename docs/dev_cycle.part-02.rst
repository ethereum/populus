Part 2: Compilation and Tester Deployment
=========================================

.. contents:: :local:

Compile
-------

Solidity compiles the source to EVM bytecode, the operations codes that will actually
run on the blockchain.

To compile, first check that solidity works on your machine. Try to get the latest version.

.. code-block:: shell

    $ solc --version
    solc, the solidity compiler commandline interface
    Version: 0.4.13+commit.0fb4cb1a.Linux.g++
    
In the project directory:

.. code-block:: shell

    $ populus compile
    
If you copy-pasted the ``Donator`` contract example, you will get:

.. code-block:: shell

  Traceback (most recent call last):
    File "/usr/local/bin/populus", line 11, in <module>
      sys.exit(main())
    File "/usr/local/lib/python3.5/dist-packages/click/core.py", line 722, in __call__
      return self.main(*args, **kwargs)
    File "/usr/local/lib/python3.5/dist-packages/click/core.py", line 697, in main
      rv = self.invoke(ctx)
    File "/usr/local/lib/python3.5/dist-packages/click/core.py", line 1066, in invoke
      return _process_result(sub_ctx.command.invoke(sub_ctx))
    File "/usr/local/lib/python3.5/dist-packages/click/core.py", line 895, in invoke
      return ctx.invoke(self.callback, **ctx.params)
    File "/usr/local/lib/python3.5/dist-packages/click/core.py", line 535, in invoke
      return callback(*args, **kwargs)
    File "/usr/local/lib/python3.5/dist-packages/click/decorators.py", line 17, in new_func
      return f(get_current_context(), *args, **kwargs)
    File "/usr/local/lib/python3.5/dist-packages/populus/cli/compile_cmd.py", line 29, in compile_cmd
      compile_project(project, watch)
    File "/usr/local/lib/python3.5/dist-packages/populus/api/compile_contracts.py", line 18, in compile_project
      _, compiled_contracts = compile_project_contracts(project)
    File "/usr/local/lib/python3.5/dist-packages/populus/compilation/__init__.py", line 54, in compile_project_contracts
      import_remappings=project.config.get('compilation.import_remappings'),
    File "/usr/local/lib/python3.5/dist-packages/populus/compilation/backends/solc_auto.py", line 52, in get_compiled_contracts
      return self.proxy_backend.get_compiled_contracts(*args, **kwargs)
    File "/usr/local/lib/python3.5/dist-packages/populus/compilation/backends/solc_standard_json.py", line 131, in get_compiled_contracts
      compilation_result = compile_standard(std_input, **command_line_options)
    File "/usr/local/lib/python3.5/dist-packages/solc/main.py", line 184, in compile_standard
      message=error_message,
  solc.exceptions.SolcError: contracts/Donator.sol:21:5: DeclarationError: Identifier not found or not unique.
  uin in_usd = msg.value * usd_rate;
  ^-^
  
      > command: `solc --standard-json`
      > return code: `0`
      > stderr:
      {"contracts":{},"errors":[{"component":"general","formattedMessage":"contracts/Donator.sol:21:5: DeclarationError: Identifier not found or not unique.\n    uin in_usd = msg.value * usd_rate;\n    ^-^\n","message":"Identifier not found or not unique.","severity":"error","type":"DeclarationError"}],"sources":{}}
  
      > stdout:

What's that? actually it's not that bad. You can ignore the Python traceback, which is just the Populus call stack until the actual
call to the compiler. 

To undersatnd what went wrong, just look at the compiler's output. The error message is quite clear:

.. code-block:: bash

  solc.exceptions.SolcError: contracts/Donator.sol:21:5: DeclarationError: Identifier not found or not unique.
  uin in_usd = msg.value * usd_rate;
  ^-^
  
Oh. Ok. ``uin in_usd`` should be ``uint in_usd``. Edit and fix it:


.. code-block:: bash

  $ nano contracts/Donator.sol

The fixed line should be:

.. code-block:: solidity

  uint in_usd = msg.value * usd_rate;
  
.. note::

  Try the `online IDE <https://remix.ethereum.org>`_ , which has great interactive compiler and web-form like interface
  to call the contract and it's funcitons.
  
  
Try to compile again:

.. code-block:: bash

  populus compile
  > Found 2 contract source files
    - contracts/Donator.sol
    - contracts/Greeter.sol
  > Compiled 2 contracts
    - contracts/Donator.sol:Donator
    - contracts/Greeter.sol:Greeter
  > Wrote compiled assets to: build/contracts.json
  
Nice. The two contracts are now compiled. Take a look at the file that Populus just added,
``build/contracts.json``. The file saves some of the compilers output, which will be useful later.

.. note::
  
    Compilation creates ``bytecode`` and ``bytecode_runtime``. The ``bytecode`` contains the ``bytecode_runtime``,
    as well as additional code. The additional code is required to deploy the runtime, but once deployed
    the runtime *is* the contract on the blockchain.
    
Tester Deployment
-----------------

You now have two compiled contracts are now ready for deployment. 

The first deployment step is to verify that it works on the ``tester`` chain. This is an ephemeral blockchain. 
It runs localy, and resets each time is starts. The state of the chain when it runs is kept only in memory,
and deleted when done. It's a great tool for a testing.

Deploy to the ``tester`` chain:

.. code-block:: bash

  $ populus deploy --chain tester Donator

  > Found 2 contract source files
    - contracts/Donator.sol
    - contracts/Greeter.sol
  > Compiled 2 contracts
    - contracts/Donator.sol:Donator
    - contracts/Greeter.sol:Greeter

  Beginning contract deployment.  Deploying 1 total contracts (1 Specified, 0 because of library dependencies).
  Donator
  Deploying Donator 
  Deploy Transaction Sent: 0xd6de5b96feb23ce2550434a46ae9c95a9ab9c76c6274cc2b1f80e0b5a6870d11 
  Waiting for confirmation... 
  
  Transaction Mined
  =================
  Tx Hash      : 0xd6de5b96feb23ce2550434a46ae9c95a9ab9c76c6274cc2b1f80e0b5a6870d11
  Address      : 0xc305c901078781c232a2a521c2af7980f8385ee9
  Gas Provided : 294313
  Gas Used     : 194313
   
  Verified contract bytecode @ 0xc305c901078781c232a2a521c2af7980f8385ee9 
  Deployment Successful.
  
When you deploy a contract Populus re-compiles *all* the contracts, but deploys only those you asked for.

Well, deployment works. Since the ``tester`` chain is not persistent, everything was deleted, but the deployment should work on persistent
chains: it's the same Ethereum protocol. Check for yourself and run the deploy again, it will re-dploy exactly the same,since
each starts from reset state.


Interim Summary
---------------

So far you have:

* Compiled the project contracts
* Verified that deployment works, using the tester chain


In the next step we will add some tests.