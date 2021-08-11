/* pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/Counters.sol";

contract EmogramMarketplace {
    using Counters for Counters.Counter;

    address[] private ownerAddresses;
    string[] public emogramIDs;

    //Royalty percentages for the creators
    uint8 private constant royalty = 1;
    mapping(address => int8) private royaltyPercentages;


    struct Auction {
        uint _auctionID;
        Counters.Counter _tokenID;
        uint _minPrice;
        uint _auctionTime;
        address payable _seller;
    }

    struct Bid {
        Counters.Counter _tokenID;
        uint auctionID;
        uint amount;
        address bidder;
    }

    struct Offer {
        Counters.Counter _tokenID;
        uint saleID;
        uint price;
        address payable seller;
    }

    mapping(uint => Bid) auctionIDToBids;
    mapping(uint => Offer) currentOffers;
    mapping(uint => Auction) currentAuctions;

    event EmogramOffered(uint indexed _tokenID, address indexed seller, uint price);
    event EmogramOnAuction(uint indexed _tokenID, address indexed seller, uint indexed auctionID, uint price, uint time);


    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    Counters.Counter private _tokenIdCounter;

    //Set up the msg.sender as the only admin and minter
    constructor(string memory name, string memory symbol) ERC721(name, symbol) {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _registerInterface(IERC721Receiver.onERC721Received.selector);
    }

    function createOffer(uint _tokenID, uint _price, uint _saleID) external {
        require(ownerOf(_tokenID) == msg.sender);

        offer = Offer(_tokenID, _saleID, _price, msg.sender);
        currentOffers[_saleID] = offer;

        emit EmogramOffered(_tokenID, msg.sender, _price);
    }

    function createAuction(uint _tokenID, uint _minPrice, uint _auctionTime, uint _auctionID) {
        require(msg.sender == ownerOf(_tokenID));

        uint endBlock = block.number + _auctionTime;

        auction = Auction(_auctionID, _tokenID, _minPrice, endBlock, msg.sender);
        currentAuctions[_auctionID] = auction;
        emit EmogramOnAuction(_tokenID, msg.sender, _auctionID, _minPrice, endBlock);
    }
        
} */