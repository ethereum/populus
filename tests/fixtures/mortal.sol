pragma solidity ^0.4.0;

import "./owned.sol"; 

contract mortal is owned { 
  function kill() public {
    suicide(msg.sender);
  }
} 
