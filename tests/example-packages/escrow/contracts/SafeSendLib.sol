pragma solidity ^0.4.0;


/// @title Library for safe sending of ether.
/// @author Piper Merriam <pipermerriam@gmail.com>
library SafeSendLib {
    /// @dev Attempts to send the specified amount to the recipient throwing an error if it fails
    /// @param recipient The address that the funds should be to.
    /// @param value The amount in wei that should be sent.
    function sendOrThrow(address recipient, uint value) returns (bool) {
        if (value > this.balance) throw;

        if (!recipient.send(value)) throw;

        return true;
    }
}
