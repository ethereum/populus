pragma solidity ^0.4.0;

import {ImportTestA} from "./ImportTestA.sol";


contract ImportTestB is ImportTestA {
  function ImportTestB() public {
  }
}
