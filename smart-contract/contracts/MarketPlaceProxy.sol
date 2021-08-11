pragma solidity ^0.8.0;


/* TODO:

    assign semi-random position of imp in storage
    to avoid collisions

 */

contract MarketPlaceProxy {

    /* 
    owner -> the owner of the contract (admin)
    isInitialized -> we use initializer instead of constructor, this needed to make sure
    the function does not run twice
    imp -> the address of the logic contract
    */
/*     
    address private owner;
    bool internal isInitialized;
    address internal imp;


    modifier onlyOwner {
        require(msg.sender == owner);
        _;
    }

    modifier isInitalized {
        require(!isInitialized, "Contract instance has already been initalized");
        _;
    }

    function initialize(address _imp) isInitialized public {
        imp = _imp;
        owner = msg.sender;
        isInitialized = true;
    }

    // function to upgrade the logic contract's address
    function upgradeTo(address) onlyOwner {
        imp = address;
    } */

}
    // Fallback function is called when we receive a function call to the proxy, as the logic function is not implemented here
    // Use external to save gas by not copying everything into the memory of the proxy contract, isntead of public
   /*  fallback() external payable {
        assembly {

            let ptr := mload(0x40)

            // copy incoming calldata
            calldatacopy(ptr, 0, calldatasize())

            // forward call to logic contract, impl is the address of the logic contract
            let result := delegatecall(gas, impl, ptr, calldatasize, 0, 0)
            let size := returndatasize

            // get the return data
            returndatacopy(ptr, 0, size)

            // forward return data back to caller
            switch result
            case 0 { revert(ptr, size) }
            default { return(ptr, size) }
        }

    }
} */