pragma solidity ^0.4.0;


contract Math {
    uint public counter;

    event Increased(uint value);
    event Decreased(uint value);

    function increment() public returns (uint) {
        return increment(1);
    }

    function increment(uint amt) public returns (uint) {
        counter += amt;
        Increased(amt);
        return counter;
    }

    function decrement() public returns (uint) {
        return decrement(1);
    }

    function decrement(uint amt) public returns (uint) {
        if (amt > counter) throw;
        counter -= amt;
        Decreased(amt);
        return counter;
    }

    function add(int a, int b) public returns (int result) {
        result = a + b;
        return result;
    }

    function multiply7(int a) public returns (int result) {
        result = a * 7;
        return result;
    }

    function return13() public returns (int result) {
        result = 13;
        return result;
    }
}
