pragma solidity ^0.8.2;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Burnable.sol";

interface IERC2981 is IERC165 {
    /// @notice Called with the sale price to determine how much royalty
    //          is owed and to whom.
    /// @param _tokenId - the NFT asset queried for royalty information
    /// @param _salePrice - the sale price of the NFT asset specified by _tokenId
    /// @return receiver - address of who should be sent the royalty payment
    /// @return royaltyAmount - the royalty payment amount for _salePrice
    function royaltyInfo(uint256 _tokenId, uint256 _salePrice) external view returns (address receiver, uint256 royaltyAmount);
    }

contract EmogramsCollectible is ERC1155, AccessControl, ERC1155Burnable {

    bytes32 public constant URI_SETTER_ROLE = keccak256("URI_SETTER_ROLE");
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BENEFICIARY_UPGRADER_ROLE = keccak256("BENEFICIARY_UPGRADER_ROLE");
    uint256 public BASE_PERCENTAGE = 750;
    address public beneficiary;
    uint256[] public emogramIds;

    constructor() ERC1155("") {

        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(URI_SETTER_ROLE, msg.sender);
        _setupRole(MINTER_ROLE, msg.sender);
        _setupRole(BENEFICIARY_UPGRADER_ROLE, msg.sender);
        beneficiary = msg.sender;
    }

    function setBeneficiary(address memory _newBeneficiary) public onlyRole(BENEFICIARY_UPGRADER_ROLE) {
        beneficiary = _newBeneficiary;
    }

    function setURI(string memory newuri) public onlyRole(URI_SETTER_ROLE) {
        _setURI(newuri);
    }

    function mint(address account, uint256 id, uint256 amount, bytes memory data)
        public
        onlyRole(MINTER_ROLE)
    {
        _mint(account, id, amount, data);
    }

    function mintBatch(address to, uint256[] memory ids, uint256[] memory amounts, bytes memory data)
        public
        onlyRole(MINTER_ROLE)
    {
        _mintBatch(to, ids, amounts, data);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC1155, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }

    function royaltyInfo(uint256 _tokenId, uint256 _salePrice) external view returns (address receiver, uint256 royaltyAmount) {
        
        uint256 roundValue = SafeMath.ceil(_salePrice, basePercent);
        console.log(roundValue);
        uint256 sevenPtFivePercent = SafeMath.div(SafeMath.mul(roundValue, BASE_PERCENTAGE), 10000);

        receiver = beneficiary;
        royaltyAmount = sevenPtFivePercent;
    }

    function createEmograms(uint256[] memory _ids, uint256[] memory _amounts) public onlyRole(MINTER_ROLE) {

        emogramIds[] = _ids;
        _mint(msg.sender, "SRT", 2970, "");
        _mintBatch(msg.sender, _ids, _amounts, "");
    }
}