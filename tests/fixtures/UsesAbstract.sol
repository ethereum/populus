pragma solidity ^0.4.0;


import {Abstract} from "./Abstract.sol";


contract UsesAbstract is Abstract {
  function doSomething() returns (bool) {
    return true;
  }
}
