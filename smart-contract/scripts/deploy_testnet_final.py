import os
import time
from brownie import EmogramsCollectible, EmogramMarketplace, EmogramsMarketplaceProxy, FounderVault, accounts, network

INITIAL_AUCTION_DURATION = 90
PRIVATE_KEY_GOERLI_MIKI = '0x0'
PRIVATE_KEY_GOERLI_CSONGOR = '0x0'
PRIVATE_KEY_GOERLI_PATR = '0x0'
PRIVATE_KEY_GOERLI_ADR = '0x0'
PRIVATE_KEY_GOERLI_DEPLOYER = 'c53152e574f8df7447caaa310622955bd9ae0f5a1b087fde9007ccbdb962f1a9'
IPFS_URI = 'https://gateway.pinata.cloud/ipfs/QmQhJB3Ep5sfjaAArr5mhJeXMcycNHeJQv8qVfkaSDaHeW/{id}.json'

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
        print("ids minted: ", i)

    # Checking total of Emogram tokens number
    y = 0
    for x in range(0, 101):
        if(emograms.balanceOf(accounts[0], x, {'from': accounts[0]}) != 0):
            y = y + emograms.balanceOf(accounts[0], x, {'from': accounts[0]})
    print("Total emograms minted: ", y)

    # setURI for IPFS hashes
    emograms.setURI(IPFS_URI, {'from': accounts[0]})

    # Approve addreses
    emograms.setApprovalForAll(marketplace, True, {'from': MIKI})
    emograms.setApprovalForAll(marketplace, True, {'from': CSONGOR})
    emograms.setApprovalForAll(marketplace, True, {'from': PATR})
    emograms.setApprovalForAll(marketplace, True, {'from': ADR})
    emograms.setApprovalForAll(marketplace, True, {'from': DEPLOYER})

def distribute_few_tokens():
    print('Distributing tokens to MIKI, CSONGOR, PATR, ADR...')
    emograms.safeTransferFrom(DEPLOYER, MIKI, 2, 1, '')
    emograms.safeTransferFrom(DEPLOYER, MIKI, 3, 1, '')
    emograms.safeTransferFrom(DEPLOYER, CSONGOR, 4, 1, '')
    emograms.safeTransferFrom(DEPLOYER, CSONGOR, 5, 1, '')
    emograms.safeTransferFrom(DEPLOYER, PATR, 6, 1, '')
    emograms.safeTransferFrom(DEPLOYER, PATR, 7, 1, '')
    emograms.safeTransferFrom(DEPLOYER, ADR, 8, 1, '')
    emograms.safeTransferFrom(DEPLOYER, ADR, 9, 1, '')


def run_initialAuction():

    # Setting initial prices 0.01 -> 0.1
    initial_auction_prices = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]
    for i in range(0, 33-len(initial_auction_prices)):
        initial_auction_prices.append(0.1)
    assert len(initial_auction_prices) == 33
    
    # Setting initial order 
    initial_order = [x for x in range(2,101)]
    random.shuffle(initial_order)
    assert len(initial_order) == 99
    marketplace.setInitialorder(initial_order)

    # Start iterating over initial auction cycles
    for idx, price in enumerate(initial_auction_prices):        
        print('Auction cycle #%s' %(idx))
        marketplace.stepAuctions(emograms, price, INITIAL_AUCTION_DURATION)
