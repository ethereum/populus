pragma solidity ^0.4.0;

import {owned} from "owned/contracts/owned.sol";

contract transferable is owned {
	event OwnerChanged(address indexed prevOwner, address indexed newOwner);

    function transferOwner(address newOwner) public onlyowner returns (bool) {
		OwnerChanged(owner, newOwner);
		owner = newOwner;
		return true;
    }
}
