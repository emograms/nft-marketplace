import os
import time
from brownie import EmogramsCollectible, EmogramMarketplace, EmogramsMarketplaceProxy, FounderVault, accounts, network

PRIVATE_KEY_GOERLI_MIKI = '0x0'
PRIVATE_KEY_GOERLI_CSONGOR = '0x0'
PRIVATE_KEY_GOERLI_PATR = '0x0'
PRIVATE_KEY_GOERLI_ADR = '0x0'
PRIVATE_KEY_GOERLI_DEPLOYER = 'c53152e574f8df7447caaa310622955bd9ae0f5a1b087fde9007ccbdb962f1a9'

def deploy_network(withProxy=True):
    print("Active Network: ")
    print(network.show_active() + "\n")

    # Init deployer address
    MIKI = accounts.add(PRIVATE_KEY_GOERLI_MIKI)
    CSONGOR = accounts.add(PRIVATE_KEY_GOERLI_CSONGOR)
    PATR = accounts.add(PRIVATE_KEY_GOERLI_PATR)
    ADR = accounts.add(PRIVATE_KEY_GOERLI_ADR)
    DEPLOYER = accounts.add(DEPLOYER_PRIVATE_KEY_GOERLI)

    # Deploying contracts
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplace.deploy({'from': accounts[0]})
    if withProxy:
        marketplace = EmogramsMarketplaceProxy.deploy()

    # Miki, Csongor, Patr, Adr
    founders = [MIKI, CSONGOR, PATR, ADR]
    founders_pct = [50, 5, 22.5, 22.5]
    founders_pct = [x*10000 for x in founders_pct]
    vault = FounderVault.deploy(founders, founders_pct, {'from': accounts[0]})
    
    print("Contracts deployed on:", network.show_active())

    # Minting Emogram NFT tokens
    mint_token_ids = list(range(2, 101))
    mint_amounts = [1 for i in range(99)]
    emograms.mintBatch(accounts[0], mint_token_ids, mint_amounts, "")

    for i in mint_token_ids:


    # setURI for IPFS hashes


    # Approve addreses
    emograms.setApprovalForAll(marketplace, True, {'from': MIKI})
    emograms.setApprovalForAll(marketplace, True, {'from': CSONGOR})
    emograms.setApprovalForAll(marketplace, True, {'from': PATR})
    emograms.setApprovalForAll(marketplace, True, {'from': ADR})
    emograms.setApprovalForAll(marketplace, True, {'from': DEPLOYER})

def run_initialAuction():
    


