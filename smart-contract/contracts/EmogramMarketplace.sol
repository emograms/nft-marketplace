pragma solidity ^0.8.0;


import "./EmogramCollectible.sol";

contract EmogramMarketplace {

address[] private ownerAddresses;
string[] public emogramIDs;
enum emogramForSaleState {ON_AUCTION, ON_SALE, NOT_FOR_SALE}
mapping(address => int8) private royaltyPercentages;

struct Emogram {
emogramForSaleState state;
uint SalePrice;
uint HighestBid;
address highestBidder;
address owner;
uint auctionExpiry; 
}

mapping(string => Emogram) public emogramMarketPlace;

}