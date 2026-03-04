// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.7.0;

contract OrderContract {
    address payable public owner;
    address payable public customer;
    address payable public courier;
    uint256 public price;
    bool public paid;
    bool public deliveryConfirmed;

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this");
        _;
    }

    modifier onlyCustomer() {
        require(msg.sender == customer, "Only customer can call this");
        _;
    }

    constructor(address payable _customer, uint256 _price) {
        owner = msg.sender;
        customer = _customer;
        price = _price;
        paid = false;
        deliveryConfirmed = false;
        courier = address(0);
    }

    function assignCourier(address payable _courier) public onlyOwner {
        require(courier == address(0), "Courier already assigned");
        require(!deliveryConfirmed, "Delivery already confirmed");
        courier = _courier;
    }

    function pay() public payable onlyCustomer {
        require(!paid, "Already paid");
        require(msg.value == price, "Incorrect payment amount");
        paid = true;
    }

    function confirmDelivery() public onlyCustomer {
        require(paid, "Order not paid");
        require(courier != address(0), "Courier not assigned");
        require(!deliveryConfirmed, "Delivery already confirmed");

        deliveryConfirmed = true;

        uint256 ownerAmount = (price * 80) / 100;
        uint256 courierAmount = price - ownerAmount;

        owner.transfer(ownerAmount);
        courier.transfer(courierAmount);
    }

    function confirmDeliveryByOwner() public onlyOwner {
        require(paid, "Order not paid");
        require(courier != address(0), "Courier not assigned");
        require(!deliveryConfirmed, "Delivery already confirmed");
        
        deliveryConfirmed = true;
        
        uint256 ownerAmount = (price * 80) / 100;
        uint256 courierAmount = price - ownerAmount;
        
        owner.transfer(ownerAmount);
        courier.transfer(courierAmount);
    }

    function isPaid() public view returns (bool) {
        return paid;
    }

    function isDeliveryConfirmed() public view returns (bool) {
        return deliveryConfirmed;
    }

    function getCourier() public view returns (address) {
        return courier;
    }
}