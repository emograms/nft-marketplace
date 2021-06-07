pragma solidity ^0.6.6;


contract EmogramMarketplace {

address[] private ownerAddresses;
string[] public emogramIDs;
enum emogramForSaleState {ON_AUCTION, ON_SALE, NOT_FOR_SALE};
mapping(ownerAddresses => int8) private royaltyPercentages;

struct Emogram {
emogramForSaleState state;
uint SalePrice;
uint HighestBid;
address highestBidder;
address owner;
uint auctionExpiry; 
};

mapping(emogramIDs => Emogram) public emogramMarketPlace;

}