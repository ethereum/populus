pragma solidity ^0.4.0;

import "./owned.sol"; 


contract immortal is owned { 
  function kill() public returns (bool no) { 
    return false;
  }
}
