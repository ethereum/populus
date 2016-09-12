#!/bin/bash
#
# Install solc 
#

set -e
set -u

if [ ! -e solc/solc ] ; then
    wget -O solc.tar.gz "https://github.com/ethereum/solidity/archive/v0.3.6.tar.gz"
    install -d solc
    cd solc
    tar -zxvf ../solc.tar.gz
    cd solidity-0.3.6
    ./scripts/install_deps.sh
    mkdir build
    cd build
    cmake .. && make
    ln -s solc/solc ../../../solc/solc-0.3.6
    echo "Geth installed at $PWD/solc"
else
    echo "Geth already installed at $PWD/solc/solc"
fi
