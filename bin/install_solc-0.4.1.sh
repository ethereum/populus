#!/bin/bash
#
# Install solc 
#

set -e
set -u

if [ ! -e solc-versions/solidity-0.4.1/build/solc/solc ] ; then
    wget -O solc.tar.gz "https://github.com/ethereum/solidity/archive/v0.4.1.tar.gz"
    install -d solc-versions
    cd solc-versions
    tar -zxvf ../solc.tar.gz
    cd solidity-0.4.1
    ./scripts/install_deps.sh
    echo "4fc6fc2ca59579fae2472df319c2d8d31fe5bde5" > commit_hash.txt
    mkdir -p build
    cd build
    cmake .. && make
    ln -fs $PWD/solc/solc ../../../solc-versions/solc-0.4.1
    chmod +x ../../../solc-versions/solc-0.4.1
    echo "Geth installed at $PWD/solc-0.4.1"
else
    echo "Geth already installed at $PWD/solc/solc-0.4.1"
fi
