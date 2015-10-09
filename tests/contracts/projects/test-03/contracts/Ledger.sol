library AccountingLib {
        struct Ledger {
                mapping (address => uint) balances;
        }

        function deposit(Ledger storage self) public {
                // check we haven't already registered
                self.balances[msg.sender] += msg.value;
        }

        function balance(Ledger storage self, address addr) constant returns (uint) {
                return self.balances[addr];
        }

        function withdraw(Ledger storage self, uint value) public {
                if (value > self.balances[msg.sender]) {
                        // insufficient balance.
                        return;
                }
                self.balances[msg.sender] -= value;
                msg.sender.send(value);
        }
}


contract PiggyBank {
        AccountingLib.Ledger accounts;

        function deposit() public {
                AccountingLib.deposit(accounts);
        }

        function checkBalance(address acct) constant returns (uint) {
                return AccountingLib.balance(accounts, acct);
        }

        function withdraw(uint value) {
                AccountingLib.withdraw(accounts, value);
        }
}
