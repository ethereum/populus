pragma solidity ^0.4.0;


contract WithNoArgumentConstructor {
  uint public data; 
  
  function WithNoArgumentConstructor() public {
    data = 3;
  }
}
