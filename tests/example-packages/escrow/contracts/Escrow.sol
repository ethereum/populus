pragma solidity ^0.4.0;


import {SafeSendLib} from "./SafeSendLib.sol";


/// @title Contract for holding funds in escrow between two semi trusted parties.
/// @author Piper Merriam <pipermerriam@gmail.com>
contract Escrow {
    using SafeSendLib for address;

    address public sender;
    address public recipient;

    function Escrow(address _recipient) payable {
        sender = msg.sender;
        recipient = _recipient;
    }

    /// @dev Releases the escrowed funds to the other party.
    /// @notice This will release the escrowed funds to the other party.
    function releaseFunds() {
        if (msg.sender == sender) {
            recipient.sendOrThrow(this.balance);
        } else if (msg.sender == recipient) {
            sender.sendOrThrow(this.balance);
        } else {
            throw;
        }
    }
}
