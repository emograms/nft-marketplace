pragma solidity ^0.8.2;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
//import "@openzeppelinUpgrades/contracts/proxy/utils/Initializable.sol";
//import "@openzeppelinUpgrades/contracts/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Burnable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/introspection/ERC165Storage.sol";

 contract EmogramMarketplace is AccessControl, ReentrancyGuard, ERC165Storage {


    bytes32 public constant FOUNDER_ROLE = keccak256("FOUNDER_ROLE");

    bytes4 constant ERC2981ID = 0x2a55205a;

    bool isTestPeriod;

    struct initAuction {
        bool isInitialAuction;
        uint256 cycle;
    }

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

    initAuction initialAuction;

    // All emograms in the marketplace
    sellItem[] public emogramsOnSale;
    auctionItem[] public emogramsOnAuction;

    //The order of the emograms during the initial auction period
    mapping(uint256 => uint256) private initialEmogramsorder;

    // Emograms in the marketplace currently up for sale or auction
    mapping(address => mapping(uint256 => bool)) public activeEmograms;
    mapping(address => mapping(uint256 => bool)) public activeAuctions;

    event EmogramAdded(uint256 indexed id, uint256 indexed tokenId, address indexed tokenAddress, uint256 askingPrice);
    event SellCancelled(address indexed sender, address indexed tokenAddress, uint256 indexed tokenId);
    event EmogramSold (uint256 indexed id, uint256 indexed tokenId, address indexed buyer, uint256 askingPrice, address seller);
    event BidPlaced(uint256 indexed id, uint256 indexed tokenId, address indexed bidder, uint256 bid);
    event AuctionCreated(uint256 indexed id, uint256 indexed tokenId, address indexed seller, address tokenAddress, uint256 startPrice, uint256 duration);
    event AuctionCanceled(uint256 indexed id, uint256 indexed tokenId, address indexed seller, address tokenAddress);
    event AuctionFinished(uint256 indexed id, uint256 indexed tokenId, address indexed highestBidder, address seller, uint256 highestBid);
    event InitialAuctionSale(uint256 indexed id, uint256 indexed tokenid, address highestBidder, uint256 highestBid);
    event InitialAuctionFinished();

    // Check if the caller is actually the owner
    modifier isTheOwner(address _tokenAddress, uint256 _tokenId, address _owner) {
        IERC1155 tokenContract = IERC1155(_tokenAddress);
        require(tokenContract.balanceOf(_owner, _tokenId) != 0, "Not owner");
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
        require(initialAuction.isInitialAuction == true, "The initial auction period has already ended");
        _;
    }

    modifier auctionNotEnded(uint256 _auctionId) {
        require(emogramsOnAuction[_auctionId].endDate > block.timestamp, "Auction has already ended");
        _;
    }

        modifier auctionEnded(uint256 _auctionId) {
        require(emogramsOnAuction[_auctionId].endDate < block.timestamp, "Auction is still ongoing");
        _;
    }

    modifier auctionNotActive(uint256 _auctionId) {
        require(activeAuctions[emogramsOnAuction[_auctionId].tokenAddress][emogramsOnAuction[_auctionId].tokenId] == false, "Auction already finished");
        _;
    }

    // Check if the item exists
    modifier itemExists(uint256 id){
        require(id <= emogramsOnSale.length && emogramsOnSale[id].sellId == id, "Could not find item");
        _;
    }
    
    modifier itemExistsAuction(uint256 id) {
        require(id <= emogramsOnAuction.length && emogramsOnAuction[id].auctionId == id, "Could not find item");
        _;
    }

    // Check if the item is actually up for sale
    modifier isForSale(uint256 id) {
        require(emogramsOnSale[id].isSold == false, "Item is already sold");
        _;
    }

    constructor(bool _isTest) {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(FOUNDER_ROLE, msg.sender);

        _registerInterface(ERC2981ID);
        isTestPeriod = _isTest;

        initialAuction.isInitialAuction = true;
        initialAuction.cycle = 0;
    }

/*     function initialize(bool _isTest) initializer public {
        __AccessControl_init();
        __UUPSUpgradeable_init();

        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(FOUNDER_ROLE, msg.sender);

        _registerInterface(ERC2981ID);
        isTestPeriod = _isTest;

        initialAuction.isInitialAuction = true;
        initialAuction.cycle = 0;
    }
 */
    function setInitialorder(uint256[99] memory _ids) 
     public
     onlyRole(FOUNDER_ROLE) {
         require(_ids.length == 99, "id length mismatch");
         for(uint256 i = 0; i < _ids.length; i++) {
             initialEmogramsorder[i] = _ids[i];
         }
    }


    // Add new founders
    function addFounder(address _newFounder)
        public
        onlyRole(DEFAULT_ADMIN_ROLE) {

            grantRole(FOUNDER_ROLE, msg.sender);
        }

    //Sell ID
    //transfers royalty to receiver
    //returns the amount to send to the seller and the seller
    function sendRoyalty(uint256 _id) 
    private 
    returns(address, uint256) {

        //Calculating royalty
        (bool succes, bytes memory result) = emogramsOnSale[_id].tokenAddress.call(abi.encodeWithSignature("royaltyInfo(uint256,uint256)", emogramsOnSale[_id].tokenId, emogramsOnSale[_id].price));
        (address receiver, uint256 royAmount) = abi.decode(result, (address, uint256));
        uint256 toSend = SafeMath.sub(emogramsOnSale[_id].price,royAmount);

        //Sending the royalty
        (bool sent, bytes memory data) = receiver.call{value: royAmount}("");
        require(sent, "Failed to send royalty");

        return (emogramsOnSale[_id].seller, toSend);

    }

    //Auction ID
    //transfers royalty to receiver
    //returns amount to send after royalty and highestbidder
    function sendRoyaltyAuction(uint256 _id)
    private
    returns(address, uint256) {

        //Calculating royalty
        (bool succes, bytes memory result) = emogramsOnAuction[_id].tokenAddress.call(abi.encodeWithSignature("royaltyInfo(uint256,uint256)", emogramsOnAuction[_id].tokenId, emogramsOnAuction[_id].highestBid));
        (address receiver, uint256 royAmount) = abi.decode(result, (address, uint256));

        uint256 toSend = emogramsOnAuction[_id].highestBid - royAmount;

        //Sending the royalty
        (bool sent, bytes memory data) = receiver.call{value: royAmount}("");
        require(sent, "Failed to send royalty");

        return (emogramsOnAuction[_id].highestBidder, toSend);
    }

    // A function to add a new Emogram to the marketplace for sale
    function addEmogramToMarket(uint256 tokenId, address tokenAddress, uint256 askingPrice) 
    hasTransferApproval(tokenAddress, tokenId)
    nonReentrant() 
    external 
    returns(uint256) {
        require(activeEmograms[tokenAddress][tokenId] == false, "Item is already up for sale");
        require(activeAuctions[tokenAddress][tokenId] == false, "Item already up for auction");
        uint256 newItemId = emogramsOnSale.length;
        emogramsOnSale.push(sellItem(newItemId, tokenAddress, tokenId, payable(msg.sender), askingPrice, false));
        activeEmograms[tokenAddress][tokenId] = true;

        assert(emogramsOnSale[newItemId].sellId == newItemId);
        emit EmogramAdded(newItemId, tokenId, tokenAddress, askingPrice);
        return newItemId;
    }

    function cancelSell(uint256 _id) 
    itemExists(_id)
    isForSale(_id)
    isTheOwner(emogramsOnSale[_id].tokenAddress, emogramsOnSale[_id].tokenId, msg.sender)
    public {
        
        emit SellCancelled(msg.sender, emogramsOnSale[_id].tokenAddress, emogramsOnSale[_id].tokenId);
        delete emogramsOnSale[_id];
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
        require(msg.sender != emogramsOnSale[id].seller, "Cannot buy own item");

        emogramsOnSale[id].isSold = true;
        activeEmograms[emogramsOnSale[id].tokenAddress][emogramsOnSale[id].tokenId] = false;
        IERC1155(emogramsOnSale[id].tokenAddress).safeTransferFrom(emogramsOnSale[id].seller, msg.sender, emogramsOnSale[id].tokenId, 1, "");

        (address receiver, uint256 toSend) = sendRoyalty(id);

        //Sending the payment
        (bool sentSucces, bytes memory dataRec) = emogramsOnSale[id].seller.call{value: toSend}("");
        require(sentSucces, "Failed to buy");

        emit EmogramSold(id, emogramsOnSale[id].tokenId, msg.sender, emogramsOnSale[id].price, emogramsOnSale[id].seller);
    }

    function createAuction(uint256 _tokenId, address _tokenAddress, uint256 _duration, uint256 _startPrice) 
    hasTransferApproval(_tokenAddress, _tokenId)
    isTheOwner(_tokenAddress, _tokenId, msg.sender)
    nonReentrant()
    public
    returns (uint256) 
    {
        require(activeAuctions[_tokenAddress][_tokenId] == false, "Emogram is already up for auction");
        require(activeEmograms[_tokenAddress][_tokenId] == false, "Item is already up for sale");
        uint256 durationToDays;

        if(isTestPeriod == true) {
            durationToDays = block.timestamp + _duration; //TODO: actually in secs
        }
        else {
            durationToDays = block.timestamp + _duration * 1 days;
         }

        emogramsOnAuction.push(auctionItem(emogramsOnAuction.length, _tokenAddress, _tokenId, payable(msg.sender), payable(msg.sender), _startPrice, _startPrice, durationToDays, true));
        activeAuctions[_tokenAddress][_tokenId] = true;

        assert(emogramsOnAuction[emogramsOnAuction.length - 1].auctionId == emogramsOnAuction.length - 1);
        emit AuctionCreated(emogramsOnAuction[emogramsOnAuction.length - 1].auctionId, _tokenId, msg.sender, _tokenAddress, _startPrice, durationToDays);

        return emogramsOnAuction[emogramsOnAuction.length - 1].auctionId;
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

        if(emogramsOnAuction[_auctionId].highestBid == emogramsOnAuction[_auctionId].startPrice) {

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
        require(emogramsOnAuction[_auctionId].seller != msg.sender, "Can't bid on your own auction!");

        if(emogramsOnAuction[_auctionId].highestBid != emogramsOnAuction[_auctionId].startPrice) {    
        (bool sent, bytes memory data) = emogramsOnAuction[_auctionId].highestBidder.call{value: emogramsOnAuction[_auctionId].highestBid}("");
        require(sent, "Failed to place bid");

        emogramsOnAuction[_auctionId].highestBidder = payable(msg.sender);
        emogramsOnAuction[_auctionId].highestBid = msg.value;

        emit BidPlaced(_auctionId, emogramsOnAuction[_auctionId].tokenId, msg.sender, msg.value);
        return _auctionId;
        }

        else {
            emogramsOnAuction[_auctionId].highestBidder = payable(msg.sender);
            emogramsOnAuction[_auctionId].highestBid = msg.value;

            emit BidPlaced(_auctionId, emogramsOnAuction[_auctionId].tokenId, msg.sender, msg.value);
            return _auctionId;
        }
    }

    function stepAuctions(address _tokenAddress, uint256 _startPrice)
    isInitialAuctionPeriod()
    onlyRole(FOUNDER_ROLE)
    payable
    external
     {
        require(initialAuction.cycle <= 33, "Max cycles already reached");

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

        for(uint256 i = (initialAuction.cycle * 3); i < (initialAuction.cycle * 3 + 3); i++) {

            createAuction(initialEmogramsorder[i], _tokenAddress, 3, _startPrice);
        }

        initialAuction.cycle = initialAuction.cycle + 1;

        if(initialAuction.cycle >= 33) {
            initialAuction.isInitialAuction = false;
            emit InitialAuctionFinished();
        }

     }

    function endAuctionWithBid(address _tokenAddress, uint256 _tokenId, uint256 _auctionId) private {

        require(emogramsOnAuction[_auctionId].highestBid != 0, "Highest bid cannot be zero in endAuctionWithBid()");

        (address receiver, uint256 toSend) = sendRoyaltyAuction(_auctionId);

        (bool sentSucces, bytes memory dataReceived) = emogramsOnAuction[_auctionId].seller.call{value: toSend}("");
        require(sentSucces, "Failed to cancel");

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
     auctionNotActive(_auctionId)
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

    function setPeriod(bool _isTest)
    onlyRole(FOUNDER_ROLE)
    public
    returns (bool) {
        isTestPeriod = _isTest;
        return isTestPeriod;
    }

    function supportsInterface(bytes4 interfaceId)
     public
     view
     override(AccessControl, ERC165Storage)
     returns (bool) {
        
        return super.supportsInterface(interfaceId);
    }
    
    receive() external payable {}
}
