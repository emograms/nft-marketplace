pragma solidity 0.8.2;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Burnable.sol";
import "@openzeppelin/contracts/interfaces/IERC2981.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC1155/IERC1155.sol";
import "@openzeppelin/contracts/utils/introspection/ERC165Storage.sol";

contract EmogramsCollectible is ERC1155, AccessControl, ERC1155Burnable, ERC165Storage {

    bytes32 public constant URI_SETTER_ROLE = keccak256("URI_SETTER_ROLE");
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BENEFICIARY_UPGRADER_ROLE = keccak256("BENEFICIARY_UPGRADER_ROLE");

    bytes4 constant ERC165ID = 0x01ffc9a7;
    bytes4 constant ERC2981ID = 0x2a55205a;

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

    string public name = "Emograms";
    string public symbol = "EGRAMS";

    mapping(uint256 => address) public ownerOfById;
    mapping(uint256 => bytes32) public hashes;


    //If the token indentified by id is redeemable this is true,
    //if the id was redeemed, it is false
    uint public redeemedCounter = 0;
    mapping(uint256 => bool) public redeemAble;
    mapping(uint256 => bytes32) public originalityHash;
    mapping(uint256 => string) public tokenURI;

    modifier notFullEmograms() {
        require(emogramId <= maxEmogramNum, "Every emogram has been minted");
        _;
    }

    modifier notYetMinted(uint256 _id) {
        require(_id != 1 || _id <= 101, "This token has already been minted");
        _;
    }

    //Checks if the operator supports the neccesary interfaces
    modifier operatorImplementsRoyalty(address _op) {

        (bool succes, bytes memory result) = _op.call(abi.encodeWithSignature("supportsInterface(bytes4)", ERC2981ID));
        bool implementsInterface2981 = abi.decode(result, (bool));

        require(implementsInterface2981 == true, "Does not support royalty interface");
        _;
    }

    modifier onlyOwner(uint256 _tokenId, address _maybeOwner) {
        require(ownerOf(_tokenId, _maybeOwner), "Not the owner");
        _;
    }

    event FungibleTokenMinted(address indexed _minter, uint256 indexed _tokenId, uint256 _amount);
    event SculptureRedeemed(uint256 indexed _tokenId, address indexed _redeemer);
    event NonFungibleTokenMinted(address indexed _minter, uint256 indexed _tokenid);
    event BeneficiaryChanged(address indexed _newBeneficiary);
    event TokensDistributedSRT(address indexed _distributor);

    constructor() ERC1155("") {

        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(URI_SETTER_ROLE, msg.sender);
        _setupRole(MINTER_ROLE, msg.sender);
        _setupRole(BENEFICIARY_UPGRADER_ROLE, msg.sender);
        beneficiary = payable(msg.sender);
        setRedeemAble();

        _registerInterface(ERC165ID);
        _registerInterface(ERC2981ID);
    }

    function setURI(string memory newuri) 
    public 
    onlyRole(URI_SETTER_ROLE) {
        _setURI(newuri);
    }

    function setTokenURI(uint256 _id, string memory _uri) 
     onlyRole(MINTER_ROLE)
     public {
         tokenURI[_id] = _uri;
     }

    function getTokenURI(uint256 _id) 
     public
     view
     returns (string memory) {
         return tokenURI[_id];
     }

    function setOrigHash(bytes32[] memory _hashes)
    onlyRole(MINTER_ROLE)
    public {
        for(uint i = 2; i < _hashes.length + 1; i++) {
            originalityHash[i] = _hashes[i-2];
        }
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
        
        ownerOfById[id] = account;
        _mint(account, id, amount, data);
    }

    function mintBatch(address to, uint256[] memory ids, uint256[] memory amounts, bytes memory data)
    public
    onlyRole(MINTER_ROLE) {
        
        _mintBatch(to, ids, amounts, data);
    }

    function safeTransferFrom(address from, address to, uint256 id, uint256 amount, bytes memory data) 
    public 
    override(ERC1155) {
        super.safeTransferFrom(from, to, id, amount, data);
        ownerOfById[id] = to;
    }

    function setRedeemAble()
    onlyRole(MINTER_ROLE)
    private {
        for(uint i = emogramId; i < maxEmogramNum + 1; i++) {
            redeemAble[i] = true;
        }
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

        mint(msg.sender, SRT, 110, "");
        return true;
    }

    // Function to distribute the SRT tokens after the initial auction
    // The distributor should have the necessary number of SRT tokens (99)
    function distributeSRT(address _distributor)
    public
    onlyRole(MINTER_ROLE)
    returns (bool) {
        require(balanceOf(_distributor, SRT) >= 99, "Not enough token to distribute");
        
        for(uint i = 2; i < 101; i++) {
            safeTransferFrom(_distributor, ownerOfById[i], SRT, 1, "");
        }
        emit TokensDistributedSRT(_distributor);
        return true;
    }

    function createEmogram() 
    public
    notFullEmograms() 
    onlyRole(MINTER_ROLE) 
    returns (uint256) {

        mint(msg.sender, emogramId, 1, "");
        emit NonFungibleTokenMinted(msg.sender, emogramId);
        redeemAble[emogramId] = true;
        emogramId = emogramId + 1;
        return emogramId;
    }

    function royaltyInfo(uint256 _tokenId, uint256 _salePrice)
    external
    view 
    returns (address receiver, uint256 royaltyAmount) {

        uint256 royaltyAmount;
        if(_salePrice > 1e76) {
                royaltyAmount = SafeMath.mul(SafeMath.div(_salePrice,10000),BASE_PERCENTAGE);
        }
        else {
                royaltyAmount = SafeMath.div(SafeMath.mul(_salePrice, BASE_PERCENTAGE),10000);
        }

        receiver = beneficiary;

        return(receiver, royaltyAmount);
    }
 
    function setApprovalForAll(address _operator, bool _approved)
    operatorImplementsRoyalty(_operator)
    public
    override(ERC1155) {

        super.setApprovalForAll(_operator, _approved);
    } 

    // TODO
    // function burn(address account, uint256 id, uint256 amount) {}

    function redeemSculp(uint256 _tokenId)
    onlyOwner(_tokenId, msg.sender)
    public {
        require(redeemAble[_tokenId] == true, "This sculpture has already been redeemed");
        require(balanceOf(msg.sender, SRT) >= 11, "Not enough SRT token to redeem");
        require(redeemedCounter < 10, "All of the 9 sculptures are redeemed");

        redeemAble[_tokenId] = false;
        redeemedCounter += 1;
        burn(msg.sender, SRT, 9);
        emit SculptureRedeemed(_tokenId, msg.sender);
    }

    function verifyOrig(bytes32 memory _origString, uint256 _tokenId)
    public 
    returns (bool) {
        if(sha256(bytes(_origString)) == originalityHash[_tokenId]) {
            return true;
         }
        else {
            return false;
         }
     }

    function supportsInterface(bytes4 interfaceId)
    public
    view
    override(ERC1155, AccessControl, ERC165Storage)
    returns (bool) {
        
        return super.supportsInterface(interfaceId);
    }
}
