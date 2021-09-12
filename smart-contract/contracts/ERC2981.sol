pragma solidity ^0.8.2;

import "@openzeppelin/contracts/utils/introspection/IERC165.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "../interfaces/IERC2981.sol";



    function ceil(uint a, uint m)
        internal
        view 
        returns (uint) {
            return ((a + m - 1) / m) * m;
    }

    function royaltyInfo(uint256 _tokenId, uint256 _salePrice)
        external
        view 
        returns (address receiver, uint256 royaltyAmount) {
        
        uint256 roundValue = ceil(_salePrice, BASE_PERCENTAGE);
        uint256 royaltyAmount = SafeMath.div(SafeMath.mul(roundValue, BASE_PERCENTAGE), 10000);

        receiver = beneficiary;
    }

        function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC1155, AccessControl)
        returns (bool) {
        
        return super.supportsInterface(interfaceId);
    }

