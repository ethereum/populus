.. _chain-api:

Chain API
=========

.. module:: populus.chain.base
.. currentmodule:: populus.chain.base

.. py:class:: BaseChain

    All chain objects inherit from the :class:`populus.chain.base.BaseChain` base
    class and expose the following API.


.. py:attribute:: BaseChain.web3

    Accessor for the :class:`~web3.Web3` instance that this chain is
    configured to use.


.. _chain-api-wait:
.. py:attribute:: BaseChain.wait

    Accessor for the :ref:`Wait API <chain-wait>`.


.. _chain-api-registrar:
.. py:attribute:: BaseChain.registrar

    Accessor for Registrar API


.. _chain-api-provider:
.. py:attribute:: BaseChain.provider

    Accessor for the Provider API
