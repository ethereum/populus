pragma solidity ^0.4.0;


contract WithConstructorArguments {
  uint public data_a;
  bytes32 public data_b; 
  
  function WithConstructorArguments(uint a, bytes32 b) public {
    data_a = a; 
    data_b = b;
  }
}
