// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract AssetVault {
    mapping(address => uint256) private _balances;

    event Deposited(address indexed user, uint256 amount);
    event Transferred(address indexed from, address indexed to, uint256 amount);

    function balanceOf(address user) external view returns (uint256) {
        return _balances[user];
    }

    function deposit() external payable {
        require(msg.value > 0, "zero deposit");
        _balances[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }

    function transferTo(address to, uint256 amount) external {
        require(to != address(0), "bad to");
        require(_balances[msg.sender] >= amount, "insufficient");
        // немає зовнішніх викликів — отже, реентрації тут немає
        _balances[msg.sender] -= amount;
        _balances[to] += amount;
        emit Transferred(msg.sender, to, amount);
    }
}
