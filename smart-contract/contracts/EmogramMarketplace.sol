pragma solidity ^0.8.2;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Burnable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

contract EmogramMarketplace is AccessControl, ReentrancyGuard {


    bytes32 public constant FOUNDER_ROLE = keccak256("FOUNDER_ROLE");

    bool public isInitialAuction = true;

    // Struct for a fixed price sell
    // sellId - Id of the sale
    // tokenAddress - the address of the token contract
    // tokenId - the Id of the NFT token on sale
    // seller - address of the seller (also current owner)
    // price - price to sell for
    // isSold - is the item already sold
    struct sellItem {
        uint256 sellId;
        address tokenAddress;
        uint256 tokenId;
        address payable seller;
        uint256 price;
        bool isSold;
    }

    // auctionId - Unique ID of the auction
    // tokenAddress - Address of the token contract
    // tokenId - Id of the NFT being auctioned
    // seller - Address of the seller
    // highestBidder - Address of the current highest bidder
    // startPrice - The starting price of the auction
    // highestBid -  The current highest bid (bid of the highestBidder)
    // duration - How long the auction is running for
    // onAuction - Is the emogram currently on auction
    struct auctionItem {
        uint256 auctionId;
        address tokenAddress;
        uint256 tokenId;
        address payable seller;
        address payable highestBidder;
        uint256 startPrice;
        uint256 highestBid;
        uint256 endDate;
        bool onAuction;
    }

    // All emograms in the marketplace
    sellItem[] public emogramsOnSale;
    auctionItem[] public emogramsOnAuction;

    //The order of the emograms during the initial auction period
    uint256[99] public initialEmogramsorder;

    // Emograms in the marketplace currently up for sale or auction
    mapping(address => mapping(uint256 => bool)) public activeEmograms;
    mapping(address => mapping(uint256 => bool)) public activeAuctions;

    event EmogramAdded(uint256 indexed id, uint256 indexed tokenId, address indexed tokenAddress, uint256 askingPrice);
    event EmogramSold (uint256 indexed id, uint256 indexed tokenId, address indexed buyer, uint256 askingPrice);
    event BidPlaced(uint256 indexed id, uint256 indexed tokenId, address indexed bidder, uint256 bid);
    event AuctionCreated(uint256 indexed id, uint256 indexed tokenId, address indexed seller, address tokenAddress, uint256 startPrice, uint256 duration);
    event AuctionCanceled(uint256 indexed id, uint256 indexed tokenId, address indexed seller, address tokenAddress);
    event AuctionFinished(uint256 indexed id, uint256 indexed tokenId, address indexed highestBidder, address seller, uint256 highestBid);
    event InitialAuctionSale(uint256 indexed id, uint256 indexed tokenid, address highestBidder, uint256 highestBid);
    event InitialAuctionFinished();

    // Check if the caller is actually the owner
    modifier isTheOwner(address _tokenAddress, uint256 _tokenId, address _owner) {
        IERC1155 tokenContract = IERC1155(_tokenAddress);
        require(tokenContract.balanceOf(_owner, _tokenId) != 0);
        _;
    }

    modifier isTheHighestBidder(address _bidder, uint256 _auctionId) {
        require(emogramsOnAuction[_auctionId].highestBidder == _bidder, "Not the highest Bidder");
        _;
    }

    // Check if marketplace has approval to sell/buy on behalf of the caller
    // TODO: Add royalty check here
    modifier hasTransferApproval (address tokenAddress, uint256 tokenId) {
        IERC1155 tokenContract = IERC1155(tokenAddress);
        require(tokenContract.isApprovedForAll(msg.sender, address(this)) == true, "No Approval");
        _;
    }

    modifier isInitialAuctionPeriod() {
        require(isInitialAuction == true, "The initial auction period has already ended");
        _;
    }

    modifier auctionNotEnded(uint256 _auctionId) {
        require(emogramsOnAuction[_auctionId].endDate > block.timestamp, "Auction has already ended.");
        _;
    }

        modifier auctionEnded(uint256 _auctionId) {
        require(emogramsOnAuction[_auctionId].endDate < block.timestamp, "Auction is still ongoing.");
        _;
    }

    // Check if the item exists
    modifier itemExists(uint256 id){
        require(id <= emogramsOnSale.length && emogramsOnSale[id].sellId == id, "could not find item");
        _;
    }
    
    modifier itemExistsAuction(uint256 id) {
        require(id <= emogramsOnAuction.length && emogramsOnAuction[id].auctionId == id, "could not find item");
        _;
    }

    // Check if the item is actually up for sale
    modifier isForSale(uint256 id) {
        require(emogramsOnSale[id].isSold == false, "item is already sold");
        _;
    }

    constructor() {

        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(FOUNDER_ROLE, msg.sender);
    }

    function setInitialorder(uint256[99] memory ids) 
     public
     onlyRole(FOUNDER_ROLE) {

         initialEmogramsorder = ids;
    }


    // Add new founders
    function addFounder(address _newFounder)
        public
        onlyRole(DEFAULT_ADMIN_ROLE) {

            grantRole(FOUNDER_ROLE, msg.sender);
        }

    // A function to add a new Emogram to the marketplace for sale
    function addEmogramToMarket(uint256 tokenId, address tokenAddress, uint256 askingPrice) 
    hasTransferApproval(tokenAddress, tokenId)
    nonReentrant() 
    external 
    returns(uint256) {
        require(activeEmograms[tokenAddress][tokenId] == false, "item is already up for sale");
        uint256 newItemId = emogramsOnSale.length;
        emogramsOnSale.push(sellItem(newItemId, tokenAddress, tokenId, payable(msg.sender), askingPrice, false));
        activeEmograms[tokenAddress][tokenId] = true;

        assert(emogramsOnSale[newItemId].sellId == newItemId);
        emit EmogramAdded(newItemId, tokenId, tokenAddress, askingPrice);
        return newItemId;
    } 

    // Buy the Emogram
    function buyEmogram(uint256 id) 
    payable  
    external
    nonReentrant() 
    itemExists(id) 
    isForSale(id) 
    {
        require(msg.value >= emogramsOnSale[id].price, "Not enough funds for purchase");
        require(msg.sender != emogramsOnSale[id].seller);

        emogramsOnSale[id].isSold = true;
        activeEmograms[emogramsOnSale[id].tokenAddress][emogramsOnSale[id].tokenId] = false;
        IERC1155(emogramsOnSale[id].tokenAddress).safeTransferFrom(emogramsOnSale[id].seller, msg.sender, emogramsOnSale[id].tokenId, 1, "");
        emogramsOnSale[id].seller.transfer(msg.value);

        emit EmogramSold(id, emogramsOnSale[id].tokenId, msg.sender, emogramsOnSale[id].price);
    }

    function createAuction(uint256 _tokenId, address _tokenAddress, uint256 _duration, uint256 _startPrice) 
    hasTransferApproval(_tokenAddress, _tokenId)
    isTheOwner(_tokenAddress, _tokenId, msg.sender)
    nonReentrant()
    public
    returns (uint256) 
    {
        require(activeAuctions[_tokenAddress][_tokenId] == false, "Emogram is already up for auction");
        uint256 durationToDays = block.timestamp + _duration; //TODO: actually in secs
        emogramsOnAuction.push(auctionItem(emogramsOnAuction.length, _tokenAddress, _tokenId, payable(msg.sender), payable(msg.sender), _startPrice, _startPrice, durationToDays, true));
        activeAuctions[_tokenAddress][_tokenId] = true;

        assert(emogramsOnAuction[emogramsOnAuction.length - 1].auctionId == emogramsOnAuction.length - 1);
        emit AuctionCreated(emogramsOnAuction.length, _tokenId, msg.sender, _tokenAddress, _startPrice, durationToDays);

        return emogramsOnAuction.length;
    }

    function cancelAuction(uint256 _auctionId, uint256 _tokenId, address _tokenAddress)
    hasTransferApproval(_tokenAddress, _tokenId)
    isTheOwner(_tokenAddress, _tokenId, msg.sender)
    auctionNotEnded(_auctionId)
    nonReentrant()
    payable
    external
    returns(uint256) 
    {
        require(activeAuctions[_tokenAddress][_tokenId] == true, "This auction doesn't exits anymore");

        if(emogramsOnAuction[_auctionId].highestBid != emogramsOnAuction[_auctionId].startPrice) {

            activeAuctions[_tokenAddress][_tokenId] = false;
            delete emogramsOnAuction[_auctionId];
            emit AuctionCanceled(_auctionId, _tokenId, msg.sender, _tokenAddress);
        }

        else {
        (bool sent, bytes memory data) = emogramsOnAuction[_auctionId].highestBidder.call{value: emogramsOnAuction[_auctionId].highestBid}("");
        require(sent, "Failed to cancel");
        activeAuctions[_tokenAddress][_tokenId] = false;
        delete emogramsOnAuction[_auctionId];

        emit AuctionCanceled(_auctionId, _tokenId, msg.sender, _tokenAddress);
        }
    }

    function PlaceBid(uint256 _auctionId, uint256 _tokenId, address _tokenAddress)
    auctionNotEnded(_auctionId)
    nonReentrant()
    payable
    external
    returns(uint256)
    {
        require(activeAuctions[_tokenAddress][_tokenId] == true, "Auction has already finished");
        require(emogramsOnAuction[_auctionId].highestBid < msg.value, "Bid too low");
        require(emogramsOnAuction[_auctionId].seller != msg.sender, "You can't bid on your own auction!");

        (bool sent, bytes memory data) = emogramsOnAuction[_auctionId].highestBidder.call{value: emogramsOnAuction[_auctionId].highestBid}("");
        require(sent, "Failed to place bid");

        emogramsOnAuction[_auctionId].highestBidder = payable(msg.sender);
        emogramsOnAuction[_auctionId].highestBid = msg.value;

        emit BidPlaced(_auctionId, emogramsOnAuction[_auctionId].tokenId, msg.sender, msg.value);
        return _auctionId;
    }

    function stepAuctions(address _tokenAddress, uint256 _startPrice)
    isInitialAuctionPeriod()
    nonReentrant()
    onlyRole(FOUNDER_ROLE)
    payable
    external
     {
        require(initialEmogramsorder.length > 0);

        if(emogramsOnAuction.length == 3) {
            for(uint i = 0; i < 3; i++) {
                if(emogramsOnAuction[i].highestBidder == msg.sender) {
                    endAuctionWithNoBid(_tokenAddress, emogramsOnAuction[i].tokenId, emogramsOnAuction[i].auctionId);
                }
                else {
                    endAuctionWithBid(_tokenAddress, emogramsOnAuction[i].tokenId, emogramsOnAuction[i].auctionId);
                }
            }
        }

        for(uint256 i = initialEmogramsorder.length; i > initialEmogramsorder.length - 3; i--) {

            createAuction(i, _tokenAddress, 3, _startPrice);
            delete initialEmogramsorder[i];
        }

     }

    function endAuctionWithBid(address _tokenAddress, uint256 _tokenId, uint256 _auctionId) private {

        require(emogramsOnAuction[_auctionId].highestBid != 0);

        (bool sent, bytes memory data) = payable(emogramsOnAuction[_auctionId].seller).call{value: emogramsOnAuction[_auctionId].highestBid}("");
        require(sent, "Failed the transaction");

        IERC1155(emogramsOnAuction[_auctionId].tokenAddress).safeTransferFrom(emogramsOnAuction[_auctionId].seller, emogramsOnAuction[_auctionId].highestBidder, emogramsOnAuction[_auctionId].tokenId, 1, "");
            
        activeAuctions[_tokenAddress][_tokenId] = false;
        delete emogramsOnAuction[_auctionId];

        emit AuctionFinished(_auctionId, _tokenId, emogramsOnAuction[_auctionId].highestBidder, emogramsOnAuction[_auctionId].seller, emogramsOnAuction[_auctionId].highestBid);
     }

    function endAuctionWithNoBid(address _tokenAddress, uint256 _tokenId, uint256 _auctionId) private {

        require(activeAuctions[_tokenAddress][_tokenId] == true);
        require(emogramsOnAuction[_auctionId].highestBid == emogramsOnAuction[_auctionId].startPrice && emogramsOnAuction[_auctionId].highestBidder == emogramsOnAuction[_auctionId].seller);

        activeAuctions[_tokenAddress][_tokenId] = false;
        delete emogramsOnAuction[_auctionId];

        emit AuctionFinished(_auctionId, _tokenId, emogramsOnAuction[_auctionId].highestBidder, emogramsOnAuction[_auctionId].seller, emogramsOnAuction[_auctionId].highestBid);         
     }

    function finishAuction(address _tokenAddress, uint256 _tokenId, uint256 _auctionId)
     auctionEnded(_auctionId)
     nonReentrant()
     hasTransferApproval(_tokenAddress, _tokenId)
     itemExistsAuction(_auctionId) 
     public
     returns (bool)
     {
        IERC1155 tokenContract = IERC1155(_tokenAddress);
        require(tokenContract.balanceOf(msg.sender, _tokenId) != 0 || emogramsOnAuction[_auctionId].highestBidder == msg.sender, "Not the owner or highest bidder");

        if(emogramsOnAuction[_auctionId].highestBid != emogramsOnAuction[_auctionId].startPrice) {

            endAuctionWithBid(_tokenAddress, _tokenId, _auctionId);
            return true;
        }

        else if(emogramsOnAuction[_auctionId].highestBid == emogramsOnAuction[_auctionId].startPrice && emogramsOnAuction[_auctionId].highestBidder == emogramsOnAuction[_auctionId].seller) {

            endAuctionWithNoBid(_tokenAddress, _tokenId, _auctionId);
            return true;
        }
     }
}
