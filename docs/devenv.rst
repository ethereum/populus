DApp development server
-----------------------

.. contents:: :local:

Introduction
^^^^^^^^^^^^

Populus provides utilies for running a development webserver for DApp
development.  These commands are accessed via ``$ populus web``

Initialization
^^^^^^^^^^^^^^

You can initialize the html/css/js portions of your project with ``$populus web init``.
Web
~~~

Populus provides utilies for running a development webserver for DApp
development.  These commands are accessed via ``$ populus web``

Initialization
^^^^^^^^^^^^^^

You can initialize the html/css/js portions of your project with ``$populus web init``.

This will create ``html`` and ``assets`` directories in your project root. As
well as an ``./html/index.html`` document.


::

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

This will create ``html`` and ``assets`` directories in your project root. As
well as an ``./html/index.html`` document.


::

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
