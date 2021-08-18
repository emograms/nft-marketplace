pragma solidity ^0.8.0;

import "@openzeppelin/contracts/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract EmogramsMarketplaceProxy is UUPSUpgradeable, AccesControl {

    //can upgrade to new implementation

    bytes32 public UPGRADER_ROLE = keccak256("UPGRADER_ROLE");
    address public upgrader;

    constructor(address _upgrader) {

        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        upgrader = _upgrader;
        _setupRole(UPGRADER_ROLE, upgrader); 
    }

    function authorizeUpgrade(address _newImplementation)
        internal 
        override 
        onlyRole(UPGRADER_ROLE) {
        
        _authorizeUpgrade(_newImplementation);
    }

    function changeUpgrader(address _newUpgradee) 
        public 
        onlyRole(DEFAULT_ADMIN_ROLE) {

        _revokeRole(UPGRADER_ROLE, upgrader);
        _grantRole(UPGRADER_ROLE, _newUpgradee);
    }

}
