pragma solidity ^0.8.6;

contract baocoin_ico {

    // Introducing the maximum number of Baocoins available for sale
    uint public max_baocoins = 1000000;

    // Introducing the USD to Baocoin conversion rate
    uint public usd_to_baocoins = 1000;

    // Introducing the total number of Baocoins that have been bought by the investors
    uint public total_baocoins_bought = 0;

    // Mapping from the investor address to its equity in Baocoins and USD
    mapping(address => uint) equity_baocoins;
    mapping(address => uint) equity_usd;

    // Checking if an investor can buy Baocoins
    modifier can_buy_baocoins(uint usd_invested) {
        require(usd_invested * usd_to_baocoins + total_baocoins_bought <= max_baocoins);
        _;
    }

    // Getting the equity in Baocoins of an investor
    function equity_in_baocoins(address investor) external view returns (uint) {
        return equity_baocoins[investor];
    }

    // Getting the equity in UD of an investor
    function equity_in_usd(address investor) external view returns (uint) {
        return equity_usd[investor];
    }

    // Buying Baocoins
    function buy_baocoins(address investor, uint usd_invested) external
    can_buy_baocoins(usd_invested) {
        uint baocoins_bought = usd_invested * usd_to_baocoins; 
        equity_baocoins[investor] += baocoins_bought;
        equity_usd[investor] = equity_baocoins[investor] / 1000;
        total_baocoins_bought += baocoins_bought;
    }

    // Selling Baocoins
    function sell_baocoins(address investor, uint baocoins_sold) external {
        equity_baocoins[investor] -= baocoins_sold;
        equity_usd[investor] = equity_baocoins[investor] / 1000;
        total_baocoins_bought -= baocoins_sold;
    }
}