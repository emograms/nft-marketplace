// SPDX-License-Identifier: MIT
pragma solidity 0.8.2;
import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Burnable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC1155/IERC1155.sol";
import "@openzeppelin/contracts/token/common/ERC2981.sol";
import "@openzeppelin/contracts/utils/introspection/ERC165Storage.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

contract EmogramsCollectible is
    ERC1155,
    AccessControl,
    ERC1155Burnable,
    ERC165Storage,
    ERC2981
{
    bytes32 public constant URI_SETTER_ROLE = keccak256("URI_SETTER_ROLE");
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BENEFICIARY_UPGRADER_ROLE =
        keccak256("BENEFICIARY_UPGRADER_ROLE");

    //Address of the SRT token contract
    ERC20Burnable public SRT;

    uint256 public constant maxEmogramNum = 99;

    // Start Id of the Non-Fungible Emograms NFT
    // Since we want a collection of 99 NFTs,
    // we need to increment this Id every time we mint
    // a new Emogram NFT
    uint256 public emogramId = 2;

    string public name = "Emograms";
    string public symbol = "EGRAMS";
    string public baseURI;

    mapping(uint256 => address) public ownerOfById;
    mapping(uint256 => bytes32) public hashes;

    //If the token indentified by id is redeemable this is true,
    //if the id was redeemed, it is false
    uint256 public redeemedCounter = 0;
    mapping(uint256 => bool) public redeemAble;
    mapping(uint256 => bytes32) public originalityHash;

    using Strings for uint256;

    modifier notFullEmograms() {
        require(emogramId <= maxEmogramNum, "Every emogram has been minted");
        _;
    }

    modifier notYetMinted(uint256 _id) {
        require(_id != 1 || _id <= 101, "This token has already been minted");
        _;
    }

    modifier onlyOwner(uint256 _tokenId, address _maybeOwner) {
        require(ownerOf(_tokenId, _maybeOwner), "Not the owner");
        _;
    }

    event SculptureRedeemed(
        uint256 indexed _tokenId,
        address indexed _redeemer
    );
    event NonFungibleTokenMinted(
        address indexed _minter,
        uint256 indexed _tokenid
    );
    event TokensDistributedSRT(address indexed distributor);
    event BaseURIChanged(string baseURI);

    constructor(
        address _beneficiary,
        uint96 _fee,
        address _SRT
    ) ERC1155("") {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(URI_SETTER_ROLE, msg.sender);
        _setupRole(MINTER_ROLE, msg.sender);
        _setupRole(BENEFICIARY_UPGRADER_ROLE, msg.sender);
        _setDefaultRoyalty(_beneficiary, _fee); //Nominator, cannot be >10000, 750 is 7.5%
        SRT = ERC20Burnable(_SRT);
        setRedeemAble();
    }

    function setBaseURI(string memory newURI)
        public
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        baseURI = newURI;
        emit BaseURIChanged(baseURI);
    }

    function tokenURI(uint256 tokenId) public view returns (string memory) {
        return
            bytes(baseURI).length > 0
                ? string(abi.encodePacked(baseURI, tokenId.toString()))
                : "";
    }

    function contractURI() public view returns (string memory) {
        return
            bytes(baseURI).length > 0
                ? string(abi.encodePacked(baseURI, "1"))
                : "";
    }

    function setOrigHash(bytes32[] memory _hashes)
        public
        onlyRole(MINTER_ROLE)
    {
        for (uint256 i = 2; i < _hashes.length + 1; i++) {
            originalityHash[i] = _hashes[i - 2];
        }
    }

    function ownerOf(uint256 _tokenId, address _maybeOwner)
        public
        view
        returns (bool)
    {
        return balanceOf(_maybeOwner, _tokenId) != 0;
    }

    function mint(
        address account,
        uint256 id,
        uint256 amount,
        bytes memory data
    ) public onlyRole(MINTER_ROLE) {
        ownerOfById[id] = account;
        _mint(account, id, amount, data);
    }

    function mintBatch(
        address to,
        uint256[] memory ids,
        uint256[] memory amounts,
        bytes memory data
    ) public onlyRole(MINTER_ROLE) {
        _mintBatch(to, ids, amounts, data);
    }

    function safeTransferFrom(
        address from,
        address to,
        uint256 id,
        uint256 amount,
        bytes memory data
    ) public override(ERC1155) {
        super.safeTransferFrom(from, to, id, amount, data);
        ownerOfById[id] = to;
    }

    function setRedeemAble() private onlyRole(MINTER_ROLE) {
        for (uint256 i = emogramId; i < maxEmogramNum + 1; i++) {
            redeemAble[i] = true;
        }
    }

    // Function to distribute the SRT tokens after the initial auction
    // The distributor should have the necessary number of SRT tokens (99)
    function distributeSRT(address _distributor)
        public
        onlyRole(MINTER_ROLE)
        returns (bool)
    {
        require(
            SRT.balanceOf(_distributor) >= 99,
            "Not enough token to distribute"
        );

        for (uint256 i = 2; i < 101; i++) {
            address sendTo = ownerOfById[i];
            SRT.transferFrom(_distributor, sendTo, 1);
        }
        emit TokensDistributedSRT(_distributor);
        return true;
    }

    function createEmogram()
        public
        notFullEmograms
        onlyRole(MINTER_ROLE)
        returns (uint256)
    {
        mint(msg.sender, emogramId, 1, "");
        emit NonFungibleTokenMinted(msg.sender, emogramId);
        redeemAble[emogramId] = true;
        emogramId = emogramId + 1;
        return emogramId;
    }

    function burn(
        address _account,
        uint256 _id,
        uint256 _amount
    ) public override(ERC1155Burnable) onlyRole(MINTER_ROLE) {
        super.burn(_account, _id, _amount);
    }

    function burnBatch(
        address _account,
        uint256[] memory _ids,
        uint256[] memory _values
    ) public override(ERC1155Burnable) onlyRole(MINTER_ROLE) {
        super.burnBatch(_account, _ids, _values);
    }

    function redeemSculp(uint256 _tokenId)
        public
        onlyOwner(_tokenId, msg.sender)
    {
        require(
            redeemAble[_tokenId] == true,
            "This sculpture has already been redeemed"
        );
        require(
            SRT.balanceOf(msg.sender) >= 33,
            "Not enough SRT token to redeem"
        );
        require(redeemedCounter < 3, "All of the 9 sculptures are redeemed");

        redeemAble[_tokenId] = false;
        redeemedCounter += 1;
        SRT.burnFrom(msg.sender, 9);
        emit SculptureRedeemed(_tokenId, msg.sender);
    }

    function verifyOrig(bytes memory _origString, uint256 _tokenId)
        public
        returns (bool)
    {
        if (
            sha256(abi.encodePacked(_origString)) == originalityHash[_tokenId]
        ) {
            return true;
        } else {
            return false;
        }
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC1155, AccessControl, ERC165Storage, ERC2981)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
