pragma solidity ^0.8.2;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Burnable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

contract EmogramMarketplace is AccessControl {


    bytes32 public constant FOUNDER_ROLE = keccak256("FOUNDER_ROLE");

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

    // All emograms in the marketplace
    sellItem[] public emogramsOnSale;

    // Emograms in the marketplace currently up for sale
    mapping(address => mapping(uint256 => bool)) activeEmograms;

    event EmogramAdded(uint256 indexed id, uint256 indexed tokenId, address indexed tokenAddress, uint256 askingPrice);
    event EmogramSold (uint256 indexed id, address indexed buyer, uint256 askingPrice);

    // Check if the caller is actually the owner

    // Check if marketplace has approval to sell/buy on behalf of the caller
    // TODO: Add royalty check here
    modifier hasTransferApproval (address tokenAddress, uint256 tokenId) {
        IERC1155 tokenContract = IERC1155(tokenAddress);
        require(tokenContract.isApprovedForAll(msg.sender, address(this)) == true);
        _;
    }

    // Check if the item exists
    modifier itemExists(uint256 id){
        require(id < emogramsOnSale.length && emogramsOnSale[id].sellId == id, "could not find item");
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


    // Add new founders
    function addFounder(address _newFounder)
        public
        onlyRole(DEFAULT_ADMIN_ROLE) {

            grantRole(FOUNDER_ROLE, msg.sender);
        }

    // A function to add a new Emogram to the marketplace for sale
    function addEmogramToMarket(uint256 tokenId, address tokenAddress, uint256 askingPrice) 
    hasTransferApproval(tokenAddress, tokenId) 
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
    itemExists(id) isForSale(id) 
    hasTransferApproval(emogramsOnSale[id].tokenAddress, emogramsOnSale[id].tokenId) {
        require(msg.value >= emogramsOnSale[id].price, "Not enough funds for purchase");
        require(msg.sender != emogramsOnSale[id].seller);

        emogramsOnSale[id].isSold = true;
        activeEmograms[emogramsOnSale[id].tokenAddress][emogramsOnSale[id].tokenId] = false;
        IERC1155(emogramsOnSale[id].tokenAddress).safeTransferFrom(emogramsOnSale[id].seller, msg.sender, emogramsOnSale[id].tokenId, 1, "");
        emogramsOnSale[id].seller.transfer(msg.value);

        emit EmogramSold(id, msg.sender, emogramsOnSale[id].price);
    }
}