pragma solidity ^0.4.0;


contract WithNoArgumentConstructor {
  uint public data; 
  
  function WithNoArgumentConstructor() {
    data = 3;
  }
}
