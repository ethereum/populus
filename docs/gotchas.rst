Solidity and Smart Contracts Gotchas
=====================================

Solidity itself is a fairly simple language, on purpose. However, the "mental model"
of smart contracts development against the blockchain is unique. We compiled a (by no means complete) list of
subtle issues which may be non-obvious, or even confusing at times,  to what you expect from a "common" programming
environment. Items are not sorted by priority.

.. role:: strike

**This is all the fun, isn't it? So here is our TOP 10, no wait 62, issues.**

[1] Everything that the contract **runs** on the blockchain, every calculation, costs money, the gas.
There is a price for each action the EVM takes on behalf of your contract. Try to offload as much computations as you can to the client.
E.g., suppose you want to calculate the average donation in a contract that collects money and counts donations.
The contract should only provide the total donations, and the number of donations, then calculate the average in the client code.

[2] Everything the contract **stores** in it's persistent storage costs money, the gas.
Try to minimise storage only to what absolutely positively is required for the contract to run. Data like derived calculations,
caching, aggregates etc, should be handled on the client.

[3] Whenever possible, use **events and logs for persistent data**.
The logs are not accessible to the contract code, and are static, so you can't use it for code execution on the block chain.
But you can read the logs from the client, and they are much cheaper.

[4] The pricing of contract **storage** is **not linear**.
There is a high initial cost to setting the storage to non zero (touching the storage). Never reset and reinitiate the storage.

[5] Everything the contracts uses for temporary memory costs money, the gas. The pricing of using **memory**, the part that is cleared once execution done (think RAM), is not linear either,
and cost per the same unit of usage increases sharply once you used a lot of memory. Try to avoid unreasonable memory usage.

[6] Even when you free storage, the gas you paid for that storage is **partially** refundable if. Don't use storage as a temporary store.

[7] Each time you **deploy** a contract, it costs money, the gas.
So the habit of pushing the whole codebase after every small commit, can cost a lot of money.
When possible, try to breakdown the functionality to small focused contracts. If you fix one, you don't have to re-deploy the others. Use library contracts (see below). Removing a contract is partially refundable, but less than deployment.

[8] No, sorry. Refunds will never exceed the gas provided in the transaction that initiated the refundable action. In fact,
**refund is maxed to 50% of the gas** in that transaction.

[9] Whenever you just send money to a contract (a transaction with value > 0), **even without calling any function**,
you run the contract's code.  The contract gets an opportunity to call other functions.
Ethereum is different from Bitcoin: even simple money sending runs code
(infact Bitcoin has a simple stack based scripts, but the common case is simple money transfers)

[10] Every contract can have one un-named function, the fallback function,
which the contract **runs when it's called even if no specific function was named in the transaction**.
This is the function you will hit when sending money in a transaction that just has value.

[11] If a contract has no fallback function, or it has one without the ``payable`` modifier, then a simple transaction
that just sends the contract Ether, without calling any function, will fail.

[12] Contracts are saved on the blockchain in a compiled EVM (ethereum virtual machine) bytecode.
There is **no way** to understand from the bytecode what the contract actually does.
The only option to verify is to get the Solidity source that the author of the contract claims is,
recompile the Source *with the same compiler version the contract on the blockchain was compiled*, and verify that this compilation
matches the bytecode on the blockchain.

[13] Never **send Eth** to a contract unless you absolutely positively trust it's author, or you verified the bytecode against a source compilation
yourself.

[14] Never **call** a contract, never call a function of a contract, unless you absolutely positively trust it's author, or you verified the bytecode against a source compilation
yourself.

[15] If you loose the ABI, you will not be able to call the contract other than the fallback function. The situation is very similar
to having a compiled executable without the source. When you compile with Populus, it saves the ABI in a project file.
The ABI tells the EVM how to correctly call the compiled bytecode and pad the arguments. Without it, there is no way to do it.
**Don't loose the ABI**.

[16] There is actually a bit convoluted way to call a contract without the ABI.  With the address ``call`` method
it's possible to call the fallback function, just provide the arguments. It's also an easy way to call
a contract if the fallback is the main function you work with. If the first argument of the ``call``
is a ``byte4`` type, **this first argument is assumed to be a function signature**, and then arguments 2..n are given to this function
(but not loosing the ABI is better). To call and forward the entire remaining gas to the callee contract use ``addr.call.value(x)()``


[17] When a contract sends money to another contract, **the called contract gets execution control** and can call your caller *before*
it returns, and before you updated your state variables. This is a *re-entry attack*. Therefore, after this second call,
your contract runs again while the state variables do *not* reflect the already sent money.
In other words: the callee can get the money, then call the sender in a state that does not tell that money was sent.
To avoid it, always
update the state variables that hold the amount which another account is allowed to get *before* you send money, and revert if the transaction failed.

[18] Moreover, the called contract can run code or recursion that will exceed the max EVM stack depth of 1024, and **trigger exception
which will bubble up to your calling contract**.

[19] Safer, and cheaper for you, to **allow withdrawal of money rather than sending it**. The gas will be paid by the beneficiary,
and you will not have to transfer execution control to another account.

[20] Contracts are **stateful**. Once you send money to a contract, it's there. You can't reinstall, or redeploy
(or restart, or patch, or fix a bug, or git pull... you get the idea).
If you didn't provide a mechanism to withdraw the funds in the first place, it's lost. If you want to update the source
of a deployed contract, you can't.
If you want to deploy a new version and didn't provide a mechanism to send the money to the new version,
you are stuck with the old one.


[21] ``call`` and ``delegatecall`` invoke other contracts, but can't catch exceptions in these contracts.
The only indication that you will get if the call excepted, is when these functions return ``false``.
This implies that providing an address of non-existent contract to ``call`` and ``delegatecall``
will **invoke nothing but still no exception**. You get ``true`` for *both* successful run *and* calling non-existent contract.
Check existence of a contract in the address, *before* the call.


[22] ``delegatecall`` is a powerful option, yet you have to be careful. It runs another contract code but **in the context of your
calling contract**. The callee has access to your calling contract Eth, storage, and the entire gas of the transaction. It can
consume all, and send the money away to another account. You can't hedge the call or limit the gas. Use ``delegatecall``
with care, typically only for library contracts that you absolutely trust.

[23] ``call`` on the client is a web3 option that behaves exactly like sending a real transaction, but it will **not change the blockchain
state**. It's kinda dry-run transaction, which is great for testing (and it's not related at all to the Solidity ``call``).
``call`` is also useful to get info from the current state, without changing it. Since no state is changed,
it runs on the local node, saving expensive gas.

[24] **Trusted** contract libraries are a good way to save gas of repeating deployments,  for code that is actually reusable.

[25] The EVM stack limit is 1024 deep. For deeply nested operations, prefer working in **steps and loops, over recursions**.

[26] Assigning variables between memory and storage **always creates a copy**, which is expensive.
Also any assignment to a state variables. Avoid it when possible.

[27] Assigning a memory variable to a storage variable always creates a pointer, which will not be aware if the **underlying state
variable changed**

[28] Don't use rounding for Eth in the contract, since **it will cost you the lost money that was rounded**.
Use the very fine grained Eth units instead.

[29] The default money unit, both in Solidity and Web3, like ``msg.value``, or getting the balance, is always **Wei**.

[30] As of solc 0.4.17 Solidity **does not have a workable decimal point type**, and your decimals will be casted to ints. If needed,
you will have to run your own fixed point calculations (many times you can retrieve the int variables, and run the decimal
calculation on the client)

[31] Once you unlock your account in a running node, typically with geth, the running process has full access to your funds. Keep it
safe. **Unlock an account only in a local, protected instance**.

[32] If you connect to a remote node with rpc, use it only for actions that do not require unlocking an account, such as reading logs,
blocks data etc. **Don't unlock accounts in remote rpc nodes**, since anybody who manages to get access to the node via the internet can use the account funds.

[33] If you have to unlock an account to deploy contracts, send transactions, etc, keep in this account **only the minimum
Eth you need** for these actions.

[34] Anybody who has the **private key** can drain the account funds, no questions asked.

[35] Anybody who has the **wallet encrypted file and it's password** can drain the account funds, no questions asked.

[36] If you use a password file to unlock the account, make sure the file is well protected with the **right permissions**.

[37] If you look at your account in sites like etherscan.io and there are funds in the account, yet locally the account
balance is 0 and geth refuses to run actions that require funds for gas - then **your local node is not synced**. You must
sync until the block with the transactions that sent money to this account.

[38] Once the contract is on the blockchain, there is **no builtin way to shut it down** or block it from responding to
messages. If the contract has a bug, an issue, a hack that let hackers steal funds, you can't shutdown, or go to "maintenance" mode, unless you provided
a mechanism for that in the contract code beforehand.

[39] Unless you provided a function that kills the contract, there is **no builtin way to delete** it from the blockchain.

[40] Scope and visibility in Solidity are only in terms of the running code. When the EVM runs your contract's code, it does care
for ``public``, ``external`` or ``internal``. The EVM doesn't use these keywords,
but visibility is enforced in the bytecode and the exposed interface (this is not just a compiler hint).
However, the scope visibility definitions have **no effect** on the
information that the blockchain exposes to the outside world.

[41] If you don't explicitly set a ``payable`` modifier to a function, it will **reject the Eth that was sent in the transaction**.
If no function has ``payable``, the contract can't accept Ether.

[42] This **is** the answer.

[43] It's **not** possible to get a list of all the ``mapping`` variable keys or values, like ``mydict.keys()`` or ``mydict.values()``
in Python. You'll have to handle such lists yourself, if required.

[44] The contract's Constructor runs only once **when the contract is created**, and can't be called again. The constructor is
optional.

[45] Inheritance in Solidity is different. Usually you have a Class, a Subclass, each is an independent object you can access.
In Solidity, the inheritance is more syntactic. In the final compilation the compiler **copies the parent class members**,
to create the bytecode of the derived contract with the *copied* members. In this context, ``private`` is just a notion of state variables and functions
that the compiler will *not* copy.

[46] Memory reads are limited to a width of 256 bits, while writes can be either 8 bits or 256 bits wide

[47] ``throw`` and ``revert`` terminate and **revert all** changes to the state and to Ether balances. The used gas is not refunded.

[48] ``function`` is  a **legit variable type**, and can be passed as an argument to another function.
If a function type variable is not initialized, calling it will obviously result in an exception.

[49] Mappings are only allowed for **state** variables

[50] ``delete`` does not actually deletes, but assigns the initial value. It's a special **kind of assignment** actually.
Deleting a local ``var`` variable that points to a state variable will except, since the "deleted" variable (the pointer)
has no initial value to reset to.

[51] Declared variables are implicitly initiated to their **initial default** value at the beginning of the function.

[52] You can declare a function as ``constant``, or the new term ``view``, which theoretically should declare a "safe"
function that does not alter the state. Yet the compiler **does not enforce it.**

[53] ``internal`` functions can be called only from the contract itself.

[54] To access an ``external`` function ``f`` from within the same contract it was declared in, use ``this.f``. In other cases you
don't need ``this`` (*this* is kinda bonus, no?)

[55] ``private`` is important only if there are **derived contracts**, where ``private`` denotes the members that
the compiler does not copy to the derived contracts. Otherwise, from within a contract, ``private`` is the same as ``internal``.

[56] ``external`` is available only for functions. ``public``, ``internal`` and ``private`` are available for both functions
and state variables. The **contract's interface** is built from it's ``external`` and ``public`` members.

[57] The compiler will **automatically** generate an accessor ("get" function) for the ``public`` state variables.

[58] ``now`` is the time stamp of the **current block**

[59] **Ethereum units** ``wei``, ``finney``, ``szabo`` or ``ether`` are reserved words, and can be used in expressions and literals.

[60] **Time units** ``seconds``, ``minutes``, ``hours``, ``days``, ``weeks`` and ``years``, are reserved words, and can be used in expressions and literals.

[61] There is **no type conversion from non-boolean** to boolean types. ``if (1) { ... }`` is not valid Solidity.

[62] The ``msg``, ``block`` and ``tx`` variables always exist in the **global namespace**, and you can use
them and their members without any prior declaration or assignment


Nice! You got here.
Yes, we know. You want more. See :ref:`writing_contracts_resources`

