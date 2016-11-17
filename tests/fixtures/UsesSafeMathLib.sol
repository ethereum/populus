pragma solidity ^0.4.0;

import {SafeMathLib} from "safe-math-lib/contracts/SafeMathLib.sol";


contract UsesSafeMathLib {
  using SafeMathLib for uint;

  function add7(uint v) constant returns (uint) {
    return v.safeAdd(7);
  }
}
