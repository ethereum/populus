.. _chain-api:

Chain API
=========

.. module:: populus.chain.base

.. py:class:: BaseChain

    All chain objects inherit from the :class:`populus.chain.base.BaseChain` base
    class and expose the following API.


.. py:attribute:: web3

    Provides access to the :class:`~web3.Web3` instance that this chain is
    configured to use.


.. py:attribute:: wait

    Accessor for to the :ref:`Wait API <chain-wait>`.


.. py:attribute:: store

    Accessor for to the :ref:`Store API <chain-store>`.


.. py:attribute:: registrar

    Accessor for to the :ref:`Registrar API <chain-registrar>`.


.. py:attribute:: provider

    Accessor for to the :ref:`Provider API <chain-provider>`.
