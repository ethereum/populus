import os
import shutil

from populus.utils.filesystem import (
    ensure_path_exists,
)

from geth.wrapper import (
    construct_test_chain_kwargs,
)

from geth.accounts import (
    create_new_account,
)

from geth.install import (
    chmod_plus_x,
)


INIT_COMMAND = (
    "geth --rpc --rpcaddr 127.0.0.1 --rpcport 8545 "
    "--rpcapi admin,debug,eth,miner,net,personal,shh,txpool,web3,ws "
    "--ws --wsaddr 127.0.0.1 --wsport 8546 "
    "--wsapi admin,debug,eth,miner,net,personal,shh,txpool,web3,ws "
    "--datadir {data_dir} --maxpeers 0 --networkid 1234 --port 30303 "
    "--ipcpath {ipc_path} --nodiscover --mine --minerthreads 1 "
    "init {genesis_path}"
)

RUN_COMMAND = (
    "geth --rpc --rpcaddr 127.0.0.1 --rpcport 8545 "
    "--rpcapi admin,debug,eth,miner,net,personal,shh,txpool,web3,ws "
    "--ws --wsaddr 127.0.0.1 --wsport 8546 "
    "--wsapi admin,debug,eth,miner,net,personal,shh,txpool,web3,ws "
    "--datadir {data_dir} --maxpeers 0 --networkid 1234 --port 30303 "
    "--ipcpath {ipc_path} --unlock {account} "
    "--password {password_path} --nodiscover --mine --minerthreads 1 "
)

GENESIS_BLOCK = '''
{
    "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
  "coinbase": "%s",
   "extraData": "0x686f727365",
   "config": {
       "daoForkBlock": 0,
     "daoForSupport": true,
    "homesteadBlock": 0
    },
   "timestamp": "0x0",
    "mixhash": "0x0000000000000000000000000000000000000000000000000000000000000000",
    "nonce": "0xdeadbeefdeadbeef",
    "alloc": {
        "%s":{
          "balance": "1000000000000000000000000000000"
      }
      },
    "gasLimit": "0x47d5cc",
    "difficulty": "0x01"
}
'''


def new_local_chain(project_dir, chain_name):
    chains_path = os.path.join(project_dir, 'chains')
    ensure_path_exists(chains_path)
    chain_dir = os.path.join(chains_path, chain_name)
    data_dir = os.path.join(chain_dir, 'chain_data')
    overrides = {
        'data_dir': data_dir,
        'ws_port': '8546',
        'rpc_port': '8545',
        'port': '30303'
    }
    geth_kwargs = construct_test_chain_kwargs(**overrides)
    password = geth_kwargs.pop('password')
    data_dir = geth_kwargs.pop('data_dir')
    account = create_new_account(data_dir, password, **geth_kwargs)
    account = account.decode('ascii')

    genesis = GENESIS_BLOCK % (account, account,)
    genesis_path = os.path.join(chain_dir, 'genesis.json')
    with open(genesis_path, 'w+') as f:
        f.write(genesis)

    password_path = os.path.join(chain_dir, 'password')
    shutil.copyfile(password, password_path)

    ipc_path = geth_kwargs['ipc_path']
    init = INIT_COMMAND.format(
        data_dir=data_dir,
        ipc_path=ipc_path,
        genesis_path=genesis_path
    )
    init_geth_path = os.path.join(chain_dir, 'init_chain.sh')
    with open(init_geth_path, 'w+') as f:
        f.write(init)
    chmod_plus_x(init_geth_path)

    run = RUN_COMMAND.format(
        data_dir=data_dir,
        ipc_path=ipc_path,
        password_path=password_path,
        account=account
    )
    run_geth_path = os.path.join(chain_dir, 'run_chain.sh')
    with open(run_geth_path, 'w+') as f:
        f.write(run)
    chmod_plus_x(run_geth_path)
