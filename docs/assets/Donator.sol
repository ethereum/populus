pragma solidity ^0.4.11;

/// TUTORIAL CONTRACT DO NOT USE IN PRODUCTION
/// @title Donations collecting contract

contract Donator {

  uint public donations_total;
  uint public donations_usd;
  uint public donations_count;
  uint public default_usd_rate;

  function Donator() {
    default_usd_rate = 350;
  }
  modifier money_sent() { if (!msg.value > 0) throw; _; }
  function donate(uint usd_rate) public payable money_sent {
      donations_total += msg.value;
      donations_count += 1;
      default_usd_rate = usd_rate;
      uin in_usd = msg.value * usd_rate;
      donations_usd += in_usd;
  }
  // fallback function
  function () payable {
    donate(default_usd_rate);
  }
 }
