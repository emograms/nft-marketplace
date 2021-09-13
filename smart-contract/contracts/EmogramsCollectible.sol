pragma solidity ^0.8.2;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Burnable.sol";
import "@openzeppelin/contracts/interfaces/IERC2981.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

contract EmogramsCollectible is ERC1155, AccessControl, ERC1155Burnable {

    bytes32 public constant URI_SETTER_ROLE = keccak256("URI_SETTER_ROLE");
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BENEFICIARY_UPGRADER_ROLE = keccak256("BENEFICIARY_UPGRADER_ROLE");

    bytes4 constant ERC165ID = 0x01ffc9a7;
    bytes4 constant ERC2981ID = "";

    // Royalty Base Percentage 7.5%
    // Royalty beneficiary address
    uint256 public BASE_PERCENTAGE = 750;
    address payable public beneficiary;

    // tokenId of the Fungible token, this won't change
    uint8 public constant SRT = 1;
    uint public constant maxEmogramNum = 99; 

    // Start Id of the Non-Fungible Emograms NFT
    // Since we want a collection of 99 NFTs, 
    // we need to increment this Id every time we mint 
    // a new Emogram NFT
    uint public emogramId = 2;

    modifier notFullEmograms() {
        require(emogramId <= maxEmogramNum, "Every emogram has been minted");
        _;
    }

    modifier notYetMinted(uint256 _id) {
        require(_id != 1 || _id <= 101, "This token has already been minted");
        _;
    }

    //Checks if the operator supports the neccesary interfaces
/*     modifier operatorImplementsRoyalty(address _op) {
        require(_op.supportsInterface(ERC2981ID) && _op.supportsInterface(ERC165ID), "Does not support royalty interface");
        _;
    } */

    event FungibleTokenMinted(address indexed _minter, uint256 indexed _tokenId, uint256 _amount);
    event NonFungibleTokenMinted(address indexed _minter, uint256 indexed _tokenid);
    event BeneficiaryChanged(address indexed _newBeneficiary);

    constructor() ERC1155("") {

        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(URI_SETTER_ROLE, msg.sender);
        _setupRole(MINTER_ROLE, msg.sender);
        _setupRole(BENEFICIARY_UPGRADER_ROLE, msg.sender);
        beneficiary = payable(msg.sender);
    }

    function setURI(string memory newuri) 
        public 
        onlyRole(URI_SETTER_ROLE) {
        _setURI(newuri);
    }

    function ownerOf(uint256 _tokenId, address _maybeOwner)
        public 
        view 
        returns (bool) {
            return balanceOf(_maybeOwner, _tokenId) != 0;
    }

    function mint(address account, uint256 id, uint256 amount, bytes memory data)
        public
        onlyRole(MINTER_ROLE) {
        
        _mint(account, id, amount, data);
    }

    function mintBatch(address to, uint256[] memory ids, uint256[] memory amounts, bytes memory data)
        public
        onlyRole(MINTER_ROLE) {
        
        _mintBatch(to, ids, amounts, data);
    }

    function setBeneficiary(address payable  _newBeneficiary)
        public 
        onlyRole(BENEFICIARY_UPGRADER_ROLE) {
        
        beneficiary = _newBeneficiary;
        emit BeneficiaryChanged(_newBeneficiary);
    }

    function createFunToken(uint256 _amount, uint8 _tokenId)
     public
     onlyRole(MINTER_ROLE) 
     returns (uint256 amount, uint8 tokenId) {

         mint(msg.sender, _tokenId, _amount, "");
         emit FungibleTokenMinted(msg.sender, _tokenId, _amount);
         return (_amount, _tokenId);
    }

    function createSRT()
    public
    notFullEmograms()
    notYetMinted(1)
    onlyRole(MINTER_ROLE)
    returns (bool) {

        mint(msg.sender, 1, 110, "");
        return true;
    }

    function createEmogram() 
    public
    notFullEmograms() 
    onlyRole(MINTER_ROLE) 
    returns (uint256) {

        mint(msg.sender, emogramId, 1, "");
        emit NonFungibleTokenMinted(msg.sender, emogramId);
        emogramId = emogramId + 1;
        return emogramId;
    }

    function createEmogramsCollection(uint256 _amount)
    public
    notFullEmograms()
    onlyRole(MINTER_ROLE)
    returns (uint256) {

        for(uint j = emogramId; j <= _amount; j++) {
            createEmogram();
        }
    }

    function royaltyInfo(uint256 _tokenId, uint256 _salePrice)
    external
    view 
    returns (address receiver, uint256 royaltyAmount) {
        
        uint256 royaltyAmount = SafeMath.div(SafeMath.mul(_salePrice, BASE_PERCENTAGE), 10000);

        receiver = beneficiary;

        return(receiver, royaltyAmount);
    }

    function supportsInterface(bytes4 interfaceId)
    public
    view
    override(ERC1155, AccessControl)
    returns (bool) {
        
        return super.supportsInterface(interfaceId);
    }
}
