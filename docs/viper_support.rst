Vyper Support
=============

Populus has support for the `vyper <https://github.com/ethereum/vyper>`_
compiler. Vyper is a python-like experimental programming language.


Known limitations
-----------------

Vyper requires Python 3.6 or above.


Installation
------------


For vyper relase version use:

.. code-block:: shell

   pip install vyper

For latest vyper development version use:

.. code-block:: shell

   pip install https://github.com/ethereum/vyper/archive/master.zip


You will see the `vyper` binary is now avialable to use.


.. code-block:: shell

    $ vyper
    usage: vyper [-h] [-f {abi,json,bytecode,bytecode_runtime,ir}]
                 [--show-gas-estimates]
                 input_file
    vyper: error: the following arguments are required: input_file


Using
-----

To use it as your compiler backend the `project.json` file must be modified.
Place a `backend` key in the `compilation` section, as shown below:


.. code-block:: json

    {
        "version": "8",
        "compilation": {
            "contracts_source_dirs": ["./contracts"],
            "import_remappings": [],
            "backend": {
                "class": "populus.compilation.backends.VyperBackend"
            }
        }
    }


This will set the Populus framework to only pick up Vyper contracts in the
configured contracts directories.
Now that everything is configured you can create a Vyper greeter contract:


.. code-block:: python

    # contracts/Greeter.v.py

    greeting: bytes <= 20


    @public
    def __init__():
        self.greeting = "Hello"


    @public
    def setGreeting(x: bytes <= 20):
        self.greeting = x


    @public
    def greet() -> bytes <= 40:
        return self.greeting


And run the default Populus tests:

.. code-block:: shell

    py.test
