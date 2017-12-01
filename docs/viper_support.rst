Viper Support
=============

Populus has support for the `viper <https://github.com/ethereum/viper>`_ compiler (a python-like experimental programming language).


Installation
------------

To install the viper compiler:


.. code-block:: shell
    pip install https://github.com/ethereum/viper/archive/master.zip


You will see the `viper` binary is now installed.


.. code-block:: shell

    $ viper
    usage: viper [-h] [-f {abi,json,bytecode,bytecode_runtime,ir}]
                 [--show-gas-estimates]
                 input_file
    viper: error: the following arguments are required: input_file


To use viper as you compiler backend you have to configure you `project.json`
file to support viper, this is done by placing a `backend` key in the `compilation`
section of your `project.json`, as shown below:


.. code-block:: json

    {
        "version": "7",
        "compilation": {
            "contracts_source_dirs": ["./contracts"],
            "import_remappings": [],
            "backend": {
                "class": "populus.compilation.backends.ViperBackend"
            }
        }
    }

This will set the populus framework to only pick up viper contracts in the
configured contracts directories.
Now that everything is configured you can create a viper greeter contract:


.. code-block:: python

    # contracts/Greeter.vy

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


And run the default populus tests:

.. code-block:: bash

    py.test
