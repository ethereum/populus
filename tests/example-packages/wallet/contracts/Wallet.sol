pragma solidity ^0.4.0;


import {SafeMathLib} from "safe-math-lib/contracts/SafeMathLib.sol";
import {owned} from "owned/contracts/owned.sol";


/// @title Contract for holding funds in escrow between two semi trusted parties.
/// @author Piper Merriam <pipermerriam@gmail.com>
contract Wallet is owned {
    using SafeMathLib for uint;

    mapping (address => uint) allowances;

    /// @dev Fallback function for depositing funds
    function() {
    }

    /// @dev Sends the recipient the specified amount
    /// @notice This will send the reciepient the specified amount.
    function send(address recipient, uint value) public onlyowner returns (bool) {
        return recipient.send(value);
    }

    /// @dev Sets recipient to be approved to withdraw the specified amount
    /// @notice This will set the recipient to be approved to withdraw the specified amount.
    function approve(address recipient, uint value) public onlyowner returns (bool) {
        allowances[recipient] = value;
        return true;
    }

    /// @dev Lets caller withdraw up to their approved amount
    /// @notice This will withdraw provided value, deducting it from your total allowance.
    function withdraw(uint value) public returns (bool) {
        allowances[msg.sender] = allowances[msg.sender].safeSub(value);
        if (!msg.sender.send(value)) throw;
        return true;
    }
}
