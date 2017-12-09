pragma solidity ^0.4.0;

contract owned {
  address owner; 
  
  function Owned() public {
    owner = msg.sender;
  }
}
