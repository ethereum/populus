pragma solidity ^0.4.0;


contract ThrowsInConstructor {
  function ThrowsInConstructor(bool shouldThrow) public { 
    if (shouldThrow) throw;
  }
}
