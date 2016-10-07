#!/bin/bash
#
# Install solc 
#

set -e
set -u

if [ ! -e solc-versions/solidity-0.4.2/build/solc/solc ] ; then
    wget -O solc.tar.gz "https://github.com/ethereum/solidity/archive/v0.4.2.tar.gz"
    install -d solc-versions
    cd solc-versions
    tar -zxvf ../solc.tar.gz
    cd solidity-0.4.2
    ./scripts/install_deps.sh
    echo "af6afb0415761b53721f89c7f65064807f41cbd3" > commit_hash.txt
    mkdir -p build
    cd build
    cmake .. && make
    ln -fs $PWD/solc/solc ../../../solc-versions/solc-0.4.2
    chmod +x ../../../solc-versions/solc-0.4.2
    echo "Geth installed at $PWD/solc-0.4.2"
else
    echo "Geth already installed at $PWD/solc/solc-0.4.2"
fi
