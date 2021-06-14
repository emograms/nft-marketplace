pragma solidity ^0.8.0;


import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Burnable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract EmogramMarketplace is ERC721, ERC721Enumerable, ERC721URIStorage, ERC721Burnable, AccessControl {
    using Counters for Counters.Counter;

    address[] private ownerAddresses;
    string[] public emogramIDs;

    //If ON_AUCTION then isForSale = true, and isFixedPrice = false
    //If ON_SALE then isForSale = true, and isFixedPrice = true
    //If NOT_FOR_SALE then isForSale = false, and isFixedPrice = false
    enum emogramForSaleState {ON_AUCTION, ON_SALE, NOT_FOR_SALE}

    //Royalty percentages for the creators
    uint8 private constant royalty = 0.1;
    mapping(address => int8) private royaltyPercentages;


    struct Offer {
    uint tokenID;
    uint minPrice; // IF ON_SALE, then minPrice is the fixed sell price, otherwise the starting price of the auction
    emogramForSaleState saleState;
    uint auctionTime;
    address onlySellTo;
    address payable seller;
    }

    struct Bid {
        uint tokenID;
        uint amount; // If ON_AUCTION, then amount is the bid amount, if it is ON_SALE, then the price
        address bidder;
    }

    //A list of the Emograms currently on sale, or on auction
    mapping (uint => Offer) public emosOnSale;

    //A list of Bids on emograms
    mapping (uint => Bid) public emogramBids;

    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    Counters.Counter private _tokenIdCounter;

    //Set up the msg.sender as the only admin and minter
    constructor(string memory name, string memory symbol) ERC721(name, symbol) {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(MINTER_ROLE, msg.sender);
    }

    function safeMint(address to) public {
        require(hasRole(MINTER_ROLE, msg.sender));
        _safeMint(to, _tokenIdCounter.current());
        _tokenIdCounter.increment();
    }

    function _baseURI() internal pure override returns (string memory) {
        return "https://ipfs.io/";
    }

    function _beforeTokenTransfer(address from, address to, uint256 tokenId)
        internal
        override(ERC721, ERC721Enumerable)
        {
            super._beforeTokenTransfer(from, to, tokenId);
        }

    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
        }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
        {
            return super.tokenURI(tokenId);
        }

    function setTokenURI(uint256 tokenId, string memory _tokenURI) 
        public {
            require(
                _isApprovedOrOwner(_msgSender(), tokenId),
                "ERC721: transfer caller is not owner nor approved"
            );
            _setTokenURI(tokenId, _tokenURI);
        }

    //TODO: Events
    function putEmogramForSale(uint _tokenId, uint _minPrice, uint _auctionTime, bool _isAuction) public {
        require(ownerOf(_tokenId) == msg.sender);
        require(emosOnSale[_tokenId].saleState == "NOT_FOR_SALE");

        emonsOnSlae[_tokenId].tokenID = _tokenId;
        emosOnSale[_tokenId].minPrice = _minPrice;
        emosOnSale[_tokenId].seller = msg.sender;
        emosOnSale[_tokenId].auctionTime = _auctionTime;
        
        if(_isAuction) {
            emosOnSale[_tokenId].saleState = "ON_AUCTION";
        }
        else {
            emosOnSale[_tokenId].saleState = "ON_SALE";
        }

    }

    //TODO: Events
    //TODO: Check if the auction period is still ongoing before changing the bid
    function placeBidOnEmogram(uint _tokenId) public payable {
        require(emosOnSale[_tokenId].saleState == "ON_AUCTION" || emosOnSale[_tokenId].saleState == "ON_SALE");
        require(msg.value >= emosOnSale[_tokenId].minPrice);

        if(emosOnSale[_tokenId].saleState == "ON_SALE") {
            _balanceOf[emosOnSale[_tokenId].seller]--;
            _balanceOf[msg.sender]++;
            _safeTransfer(emosOnSale[_tokenId].seller, msg.sender, _tokenId);
            emosOnSale[_tokenId].seller.transfer(msg.value * (1 - royalty));
        }

        if(emosOnSale[_tokenId].saleState == "ON_AUCTION") {
            if(emogramBids[_tokenId].minPrice < msg.value) {
                emogramBids[_tokenId].bidder.transfer(emogramBids[_tokeId].minPrice);
                emogramBids[_tokenId] = Bid(_tokenId, msg.value, msg.sender);
            }
            else {
                throw;
            }
        }
    }
        
    function supportsInterface(bytes4 interfaceId)
            public
            view
            override(ERC721, ERC721Enumerable, AccessControl)
            returns (bool)
        {
            return super.supportsInterface(interfaceId);
        }

    

}