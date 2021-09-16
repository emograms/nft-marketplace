import os
import time
from brownie import EmogramsCollectible, EmogramMarketplace, EmogramsMarketplaceProxy, FounderVault, accounts, network

# VARS
INITIAL_AUCTION_DURATION = 90
IPFS_URI = 'https://gateway.pinata.cloud/ipfs/QmQhJB3Ep5sfjaAArr5mhJeXMcycNHeJQv8qVfkaSDaHeW/{id}.json'

# WALLETS
PRIVATE_KEY_GOERLI_MIKI = '3a8bb854c7a86d950c0d3e0b5b1bbcd3912389a95fa530e46c911fe1de099808' #'0xFe594E862c3ce76E192997EABFC41Afd7C975b52'
PRIVATE_KEY_GOERLI_CSONGOR = '7890e57df5d235ca4a5065341467d18276293f7066bf96e7e9a88c6f89737c67' #'0x76cA42252508c0AD52bf7936dC3eabb82cF9872e'
PRIVATE_KEY_GOERLI_PATR = 'fd290876475f82321cb0c142893c150fda939e9a3a3360715456f734eaef8831' #'0xE7E8FB1932084E3BbE382EbaCdc16D835B30216F'
PRIVATE_KEY_GOERLI_ADR = '5ffe2515807d0ace67c342183c6aa506f25553d7fa0e93ceeb4d9b77b55128a2' #'0xA558c9148846F17AcD9E99D8a8D0D1ECdCf0c7fA'
PRIVATE_KEY_GOERLI_DEPLOYER = 'c53152e574f8df7447caaa310622955bd9ae0f5a1b087fde9007ccbdb962f1a9'

def deploy_network(withProxy=True, testMode=False):
    print("Active Network: ")
    print(network.show_active() + "\n")

    # Init deployer address
    MIKI = accounts.add(PRIVATE_KEY_GOERLI_MIKI)
    CSONGOR = accounts.add(PRIVATE_KEY_GOERLI_CSONGOR)
    PATR = accounts.add(PRIVATE_KEY_GOERLI_PATR)
    ADR = accounts.add(PRIVATE_KEY_GOERLI_ADR)
    DEPLOYER = accounts.add(PRIVATE_KEY_GOERLI_DEPLOYER)

    # Deploying contracts
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplace.deploy(testMode, {'from': accounts[0]})
    if withProxy:
        marketplace = EmogramsMarketplaceProxy.deploy()

    # Miki, Csongor, Patr, Adr
    founders = [MIKI, CSONGOR, PATR, ADR]
    founders_pct = [50, 5, 22.5, 22.5]
    founders_pct = [x*10000 for x in founders_pct]
    vault = FounderVault.deploy(founders, founders_pct, {'from': accounts[0]})
    
    print("Contracts deployed on:", network.show_active())

    # Set beneficiary on EmogramsCollectible
    emograms.setBeneficiary(vault)

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

    # Emogram Tokens
    emograms.safeTransferFrom(DEPLOYER, MIKI, 2, 1, '')
    emograms.safeTransferFrom(DEPLOYER, MIKI, 3, 1, '')
    emograms.safeTransferFrom(DEPLOYER, CSONGOR, 4, 1, '')
    emograms.safeTransferFrom(DEPLOYER, CSONGOR, 5, 1, '')
    emograms.safeTransferFrom(DEPLOYER, PATR, 6, 1, '')
    emograms.safeTransferFrom(DEPLOYER, PATR, 7, 1, '')
    emograms.safeTransferFrom(DEPLOYER, ADR, 8, 1, '')
    emograms.safeTransferFrom(DEPLOYER, ADR, 9, 1, '')

    # SRT Tokens
    emograms.safeTransferFrom(DEPLOYER, MIKI, 1, 2, '')
    emograms.safeTransferFrom(DEPLOYER, CSONGOR, 1, 2, '')
    emograms.safeTransferFrom(DEPLOYER, PATR, 1, 2, '')
    emograms.safeTransferFrom(DEPLOYER, ADR, 1, 2, '')


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
