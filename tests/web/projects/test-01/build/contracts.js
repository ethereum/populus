
var contracts = contracts || {};

function makeContracts() {
    var contractData = {
    "Example": {
        "code": "0x60606040525b5b600a8060136000396000f30060606040526008565b00",
        "info": {
            "abiDefinition": [
                {
                    "inputs": [],
                    "type": "constructor"
                }
            ],
            "compilerVersion": "0.1.1-054b3c3c",
            "developerDoc": {
                "methods": {}
            },
            "language": "Solidity",
            "languageVersion": "0",
            "source": "contract Example {\n        function Example() {\n        }\n}\n",
            "userDoc": {
                "methods": {}
            }
        }
    }
};
    var contractNames = Object.keys(contractData);
    for (var i=0; i < contractNames.length; i++) {
        contractName = contractNames[i];
        contracts[contractName] = web3.eth.contract(contractData[contractName].info.abiDefinition);
    }
};
makeContracts();
