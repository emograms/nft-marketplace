pragma solidity ^0.6.6;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract EmogramCollectible is ERC721 {

    uint256 public tokenCounter;

    constructor() public ERC721 ("EmogramsTEST", "EMT") {
        tokenCounter = 0;
    }

    function createEmogramCollectible(string memory tokenURI) public returns (uint256) {

        uint256 newItemId = tokenCounter;
        _safeMint(msg.sender, newItemId);
        _setTokenURI(newItemId, tokenURI);
        tokenCounter = tokenCounter + 1;
        return newItemId;
    }
}