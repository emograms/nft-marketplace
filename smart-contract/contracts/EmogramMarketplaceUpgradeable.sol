pragma solidity 0.8.2;

import "@openzeppelinUpgrades/contracts/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelinUpgrades/contracts/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelinUpgrades/contracts/proxy/utils/Initializable.sol";
import "@openzeppelinUpgrades/contracts/security/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelinUpgrades/contracts/utils/introspection/ERC165StorageUpgradeable.sol";


//TODO: Add setter/getter func. for defaultIncrement, add increment param in funcs.

 contract EmogramMarketplaceUpgradeable is 
 Initializable, UUPSUpgradeable, ERC165StorageUpgradeable, ReentrancyGuardUpgradeable, AccessControlUpgradeable {

     using SafeERC20 for IERC20;
     using SafeMath for uint256;

    IERC20 public weth;

    bytes32 public constant FOUNDER_ROLE = keccak256("FOUNDER_ROLE");
    bytes32 public constant UPGRADER_ROLE = keccak256("UPGRADER_ROLE");
    
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

    // Emograms in the marketplace currently up for sale or auction
    mapping(address => mapping(uint256 => bool)) public activeEmograms;
    mapping(address => mapping(uint256 => bool)) public activeAuctions;

    bool isTestPeriod;

    // Events
    event EmogramAdded(uint256 indexed id, uint256 indexed tokenId, address indexed tokenAddress, uint256 askingPrice);
    event SellCancelled(address indexed sender, address indexed tokenAddress, uint256 indexed tokenId);
    event EmogramSold (uint256 indexed id, uint256 indexed tokenId, address indexed buyer, uint256 askingPrice, address seller);
    event BidPlaced(uint256 indexed id, uint256 indexed tokenId, address indexed bidder, uint256 bid);
    event AuctionCreated(uint256 indexed id, uint256 indexed tokenId, address indexed seller, address tokenAddress, uint256 startPrice, uint256 duration);
    event AuctionCanceled(uint256 indexed id, uint256 indexed tokenId, address indexed seller, address tokenAddress);
    event AuctionFinished(uint256 indexed id, uint256 indexed tokenId, address indexed highestBidder, address seller, uint256 highestBid);

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
    modifier hasTransferApproval (address tokenAddress, uint256 tokenId) {
        IERC1155 tokenContract = IERC1155(tokenAddress);
        require(tokenContract.isApprovedForAll(msg.sender, address(this)) == true, "No Approval");
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

    modifier AuctionActive(uint256 _auctionId) {
        require(activeAuctions[emogramsOnAuction[_auctionId].tokenAddress][emogramsOnAuction[_auctionId].tokenId] == true, "Auction already finished");
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

    function initialize(bool _isTest, address _weth) initializer public {
        
        __AccessControl_init();
        __UUPSUpgradeable_init();
        __ReentrancyGuard_init();
        __ERC165Storage_init();

        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(FOUNDER_ROLE, msg.sender);
        _setupRole(UPGRADER_ROLE, msg.sender);

        isTestPeriod = _isTest;
        weth = IERC20(_weth);
    }

    // Add new founders
    function addFounder(address _newFounder)
    public
    onlyRole(DEFAULT_ADMIN_ROLE) {

            grantRole(FOUNDER_ROLE, _newFounder);
        }

    function emogramsOnSaleLength()
    public
    view
    returns (uint256) {
            return emogramsOnSale.length;
        }

    function emogramsOnAuctionLength()
    public
    view
    returns (uint256) {
            return emogramsOnAuction.length;
        }

    function getSaleArray()
    public
    view
    returns (sellItem[] memory) {
          return emogramsOnSale;
      }

    function getAuctionArray()
    public
    view
    returns (auctionItem[] memory) {
          return emogramsOnAuction;
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
        //Seller might need changing to this contracts' address, right now,
        //we receive payment before successful sale and NFT transfer, from the buyer
        weth.safeTransferFrom(weth, msg.sender, receiver, royAmount);
        
        return (emogramsOnSale[_id], toSend);
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
        weth.safeTransferFrom(weth, emogramsOnAuction[_id].highestBidder, receiver, royAmount);

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
        activeEmograms[emogramsOnSale[_id].tokenAddress][emogramsOnSale[_id].tokenId] = false;
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
        weth.safeTransferFrom(weth, emogramsOnSale[id].seller, msg.sender, toSend);
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
            durationToDays = block.timestamp + _duration;
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

        //If the highestBidder is the seller, then there were no bids, so nothing to send

        if(emogramsOnAuction[_auctionId].highestBidder == emogramsOnAuction[_auctionId].seller) {

            activeAuctions[_tokenAddress][_tokenId] = false;
            delete emogramsOnAuction[_auctionId];
            emit AuctionCanceled(_auctionId, _tokenId, msg.sender, _tokenAddress);
        }
        
        //Else we send the weth (highestBid) back to the highestBidder from the marketplace contract
        else {

            weth.safeTransferFrom(weth, address(this), emogramsOnAuction[_auctionId].highestBidder, emogramsOnAuction[_auctionId].highestBid);

            activeAuctions[_tokenAddress][_tokenId] = false;
            delete emogramsOnAuction[_auctionId];

            emit AuctionCanceled(_auctionId, _tokenId, msg.sender, _tokenAddress);
        }
    }

    function PlaceBid(uint256 _auctionId, uint256 _tokenId, address _tokenAddress)
    auctionNotEnded(_auctionId)
    nonReentrant()
    payable
    public
    returns(uint256)
    {
        require(activeAuctions[_tokenAddress][_tokenId] == true, "Auction has already finished");
        require(emogramsOnAuction[_auctionId].highestBid <= weth.balanceOf(msg.sender), "Not enough wETH to bid");
        require(emogramsOnAuction[_auctionId].seller != msg.sender, "Can't bid on your own auction!");

        // since the seller can't bid on their own auction, this if only runs when no previous bid has been placed
        if(emogramsOnAuction[_auctionId].highestBidder == emogramsOnAuction[_auctionId].seller) {    

            emogramsOnAuction[_auctionId].highestBidder = payable(msg.sender);
            uint256 memory amount = emogramsOnAuction[_auctionId].highestBid;
            emogramsOnAuction[_auctionId].highestBid = weth.safeTransferFrom(weth, msg.sender, address(this), amount);

            emit BidPlaced(_auctionId, emogramsOnAuction[_auctionId].tokenId, msg.sender, msg.value);
            return _auctionId;
        }

        else {

            // IF the seller is not the highest bidder, that means someone already made a bid
            // so we rew. the msg.value to be bigger than the current bid, and not equal or bigger

            require(emogramsOnAuction[_auctionId].highestBid <= weth.balanceOf(msg.sender), "Not enough wETH to bid");

            //we send the previous highest bid back
            weth.safeTransferFrom(weth, address(this), emogramsOnAuction[_auctionId].highestBidder, emogramsOnAuction[_auctionId].highestBid); 

            //set the new highest bid and bidder
            emogramsOnAuction[_auctionId].highestBidder = payable(msg.sender);
            emogramsOnAuction[_auctionId].highestBid = msg.value;

            emit BidPlaced(_auctionId, emogramsOnAuction[_auctionId].tokenId, msg.sender, msg.value);
            return _auctionId;
        }
    }

    function endAuctionWithBid(address _tokenAddress, uint256 _tokenId, uint256 _auctionId) private {

        require(emogramsOnAuction[_auctionId].highestBid != 0, "Highest bid cannot be zero in endAuctionWithBid()");

        //Send royalty
        (address receiver, uint256 toSend) = sendRoyaltyAuction(_auctionId);

        //Send payment to seller from highestBidder
        weth.safeTransferFrom(weth, emogramsOnAuction[_auctionId].highestBidder, emogramsOnAuction[_auctionId].seller, toSend);

        //Transfer NFT from seller to highestBidder
        IERC1155(emogramsOnAuction[_auctionId].tokenAddress).safeTransferFrom(emogramsOnAuction[_auctionId].seller, emogramsOnAuction[_auctionId].highestBidder, emogramsOnAuction[_auctionId].tokenId, 1, "");

        //Cleanup    
        activeAuctions[_tokenAddress][_tokenId] = false;
        emit AuctionFinished(_auctionId, _tokenId, emogramsOnAuction[_auctionId].highestBidder, emogramsOnAuction[_auctionId].seller, emogramsOnAuction[_auctionId].highestBid);
        delete emogramsOnAuction[_auctionId];
     }

    function endAuctionWithNoBid(address _tokenAddress, uint256 _tokenId, uint256 _auctionId) private {

        require(activeAuctions[_tokenAddress][_tokenId] == true);
        require(emogramsOnAuction[_auctionId].highestBid == emogramsOnAuction[_auctionId].startPrice && emogramsOnAuction[_auctionId].highestBidder == emogramsOnAuction[_auctionId].seller);

        activeAuctions[_tokenAddress][_tokenId] = false;
        emit AuctionFinished(_auctionId, _tokenId, emogramsOnAuction[_auctionId].highestBidder, emogramsOnAuction[_auctionId].seller, emogramsOnAuction[_auctionId].highestBid);     
        delete emogramsOnAuction[_auctionId];    
     }

    function finishAuction(address _tokenAddress, uint256 _tokenId, uint256 _auctionId)
    auctionEnded(_auctionId)
    AuctionActive(_auctionId)
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

    function _authorizeUpgrade(address) 
    internal 
    override
    onlyRole(UPGRADER_ROLE) {}

    function supportsInterface(bytes4 interfaceId)
    public
    view
    override(AccessControlUpgradeable, ERC165StorageUpgradeable)
    returns (bool) {
        
        return super.supportsInterface(interfaceId);
    }
}
