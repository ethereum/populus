contract Wallet {
    mapping (address => uint) public balanceOf;

    function deposit() {
        balanceOf[msg.sender] += 1;
    }

    function withdraw(uint value) {
        if (balanceOf[msg.sender] < value) throw;
        balanceOf[msg.sender] -= value;
        if (!msg.sender.call.value(value)()) throw;
    }
}
