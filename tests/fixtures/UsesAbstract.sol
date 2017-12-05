pragma solidity ^0.4.0;


import {Abstract} from "./Abstract.sol";


contract UsesAbstract is Abstract {
  function doSomething() public returns (bool) {
    return true;
  }
}
