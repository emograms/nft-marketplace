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


contract TestCollectible is
    ERC1155,
    AccessControl,
    ERC1155Burnable,
    ERC165Storage,
    ERC2981
{
    bytes32 public constant URI_SETTER_ROLE = keccak256("URI_SETTER_ROLE");
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BENEFICIARY_UPGRADER_ROLE = keccak256("BENEFICIARY_UPGRADER_ROLE");

    string public contracturi;

    string public name = "Testograms";
    string public symbol = "TESTGRAM";
    string public baseURI;

    mapping(uint256 => address) public ownerOfById;
    mapping(uint256 => bytes32) public hashes;

    bool public isClosed;

    using Strings for uint256;

    modifier notYetMinted(uint256 _id) {
        require(_id != 1 || _id <= 101, "This token has already been minted");
        _;
    }

    modifier onlyOwner(uint256 _tokenId, address _maybeOwner) {
        require(ownerOf(_tokenId, _maybeOwner), "Not the owner");
        _;
    }

    modifier notClosed() {
        require(isClosed == false, "The contract is no longer operational");
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
        bool _closed
    ) ERC1155("") {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(URI_SETTER_ROLE, msg.sender);
        _setupRole(MINTER_ROLE, msg.sender);
        _setupRole(BENEFICIARY_UPGRADER_ROLE, msg.sender);
        _setDefaultRoyalty(_beneficiary, _fee); //Nominator, cannot be >10000, 750 is 7.5%
        isClosed = _closed;
    }

    function setBaseURI(string memory newURI)
        public
        onlyRole(DEFAULT_ADMIN_ROLE)
        notClosed()
    {
        baseURI = newURI;
        emit BaseURIChanged(baseURI);
    }

    function setContractURI(string memory _contractURI) public 
    notClosed()
    {
        contracturi = _contractURI;
    }

    function contractURI() public view returns (string memory) 
    {
        return contracturi;
    }

    function setURI(string memory _newuri) 
        public
        onlyRole(URI_SETTER_ROLE)
        notClosed() 
    {
        _setURI(_newuri);
    }

    function ownerOf(uint256 _tokenId, address _maybeOwner)
        public
        view
        notClosed()
        returns (bool)
    {
        return balanceOf(_maybeOwner, _tokenId) != 0;
    }

    function mint(
        address account,
        uint256 id,
        uint256 amount,
        bytes memory data
    ) public onlyRole(MINTER_ROLE) 
            notClosed()
    {
        ownerOfById[id] = account;
        _mint(account, id, amount, data);
    }

    function mintBatch(
        address to,
        uint256[] memory ids,
        uint256[] memory amounts,
        bytes memory data
    ) public onlyRole(MINTER_ROLE) 
            notClosed()
    {
        _mintBatch(to, ids, amounts, data);
    }

    function safeTransferFrom(
        address from,
        address to,
        uint256 id,
        uint256 amount,
        bytes memory data
    ) public override(ERC1155) notClosed()
    {
        super.safeTransferFrom(from, to, id, amount, data);
        ownerOfById[id] = to;
    }

    function burn(
        address _account,
        uint256 _id,
        uint256 _amount
    ) public override(ERC1155Burnable) onlyRole(MINTER_ROLE) notClosed(){
        super.burn(_account, _id, _amount);
    }

    function burnBatch(
        address _account,
        uint256[] memory _ids,
        uint256[] memory _values
    ) public override(ERC1155Burnable) onlyRole(MINTER_ROLE) notClosed(){
        super.burnBatch(_account, _ids, _values);
    }

    function kill(address payable _benef) onlyRole(DEFAULT_ADMIN_ROLE) notClosed() public {
        isClosed = true;
        selfdestruct(_benef);
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