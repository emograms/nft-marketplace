pragma solidity ^0.8.2;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract FounderVault is AccessControl, ReentrancyGuard {

    uint256 totalContents;
    
    bytes32 public constant PERC_SETTER_ROLE = keccak256("PERC_SETTER_ROLE");
    bytes32 public constant WITHDRAWER_ROLE = keccak256("WITHDRAWER_ROLE");

    address payable[] public Founders;

    mapping(address => uint256) Percentages;

    event Withdrawal(address indexed caller, uint256 amount);
    event FounderAdded(address indexed caller, address indexed newFounder);
    event NewBatchFounders(address indexed caller);

    constructor(address payable[] memory _founders, uint256[] memory _percentages) {
        
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(PERC_SETTER_ROLE, msg.sender);
        _setupRole(WITHDRAWER_ROLE, msg.sender);

        require(_founders.length == _percentages.length, "Founder and percentages size not equal");
        Founders = _founders;

        for(uint i = 0; i < _founders.length; i++) {
            Percentages[_founders[i]] = _percentages[i];
        }

        totalContents = 0;

    }

    function withdraw()
    nonReentrant() 
    onlyRole(WITHDRAWER_ROLE)
    public {

        require(totalContents == address(this).balance, "Balance inconsistent!");
        require(totalContents != 0, "Vault empty!");
        
        for(uint i = 0; i < Founders.length; i++) {
            uint256 toPay = SafeMath.div(SafeMath.mul(totalContents, Percentages[Founders[i]]), 10000);

            (bool sent, bytes memory data) = Founders[i].call{value: toPay}("");
            require(sent, "Failed to withdraw");
        }

        emit Withdrawal(msg.sender, totalContents);
    }

    function setPercentages(uint256[] memory _newPercentages, address payable[] memory _Founders)  
    onlyRole(PERC_SETTER_ROLE)
    nonReentrant() 
    public {

        require(_newPercentages.length == _Founders.length, "Founder and percentages list not equal length");

        for(uint i = 0; i < _Founders.length; i++) {
            Percentages[_Founders[i]] = _newPercentages[i];
        }
    }

    function resetFounders(address payable[] memory _newFounders) 
    nonReentrant()
    onlyRole(DEFAULT_ADMIN_ROLE) 
    public {

        Founders = _newFounders;

        emit NewBatchFounders(msg.sender);
    }

    function addFounder(address payable  _newFounder) 
    public 
    onlyRole(DEFAULT_ADMIN_ROLE) {

        Founders.push(_newFounder);

        emit FounderAdded(msg.sender, _newFounder);
    }

    function checkContents() 
    nonReentrant() 
    public
    returns (bool) {

        return (totalContents == address(this).balance);
    }

    receive() 
    payable 
    external {

        totalContents = totalContents + msg.value;
    }
}