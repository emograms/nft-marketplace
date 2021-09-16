pragma solidity ^0.8.2;

import "@openzeppelin/contracts/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract EmogramsMarketplaceProxy is UUPSUpgradeable, AccessControl {

    //can upgrade to new implementation

    bytes32 public UPGRADER_ROLE = keccak256("UPGRADER_ROLE");
    address public upgrader;

    constructor(address _upgrader, address initialImplementation) {

        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        upgrader = _upgrader;
        _setupRole(UPGRADER_ROLE, upgrader);
        _upgradeTo(initialImplementation); 
    }

    function _authorizeUpgrade(address _newImplementation)
        internal
        override 
        onlyRole(UPGRADER_ROLE) {}

    function changeUpgrader(address _newUpgradee) 
        public 
        onlyRole(DEFAULT_ADMIN_ROLE) {

        revokeRole(UPGRADER_ROLE, upgrader);
        grantRole(UPGRADER_ROLE, _newUpgradee);
    }

}
