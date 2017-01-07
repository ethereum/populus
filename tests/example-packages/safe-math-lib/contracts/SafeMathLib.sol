pragma solidity ^0.4.0;


/// @title Safe Math Library
/// @author Piper Merriam <pipermerriam@gmail.com>
library SafeMathLib {
    /// @dev Subtracts b from a, throwing an error if the operation would cause an underflow.
    /// @param a The number to be subtracted from
    /// @param b The amount that should be subtracted
    function safeAdd(uint a, uint b) returns (uint) {
        if (a + b > a) {
            return a + b;
        } else {
            throw;
        }
    }

    /// @dev Adds a and b, throwing an error if the operation would cause an overflow.
    /// @param a The first number to add
    /// @param b The second number to add
    function safeSub(uint a, uint b) returns (uint) {
        if (b <= a) {
            return a - b;
        } else {
            throw;
        }
    }
}
