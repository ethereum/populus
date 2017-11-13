pragma solidity ^0.4.11;

/// TUTORIAL CONTRACT DO NOT USE IN PRODUCTION
/// @title Donations collecting contract

contract Donator2 {

  uint public donations_total;
  uint public donations_usd;
  uint public donations_count;
  uint public default_usd_rate;

  function Donator2() {
    default_usd_rate = 350;
  }
  modifier money_sent() { if (!(msg.value > 0)) throw; _; }
  function donate(uint usd_rate) public payable money_sent {
      donations_total += msg.value;
      donations_count += 1;
      default_usd_rate = usd_rate;
      uint in_usd = msg.value * usd_rate / 10**18;
      donations_usd += in_usd;
  }
  // fallback function
  function () payable {
    donate(default_usd_rate);
  }
  //demo only allows ANYONE to withdraw
  function withdrawAll() external {
      require(msg.sender.send(this.balance));
        }
 }
