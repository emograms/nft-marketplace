import os
import time
from brownie import EmogramsCollectible, EmogramMarketplace, EmogramsMarketplaceProxy, FounderVault, accounts, network

MIKI = '0x0'
CSONGOR = '0x0'
PATR = '0x0'
ADR = '0x0'


def main():
    dev = accounts.load(0)
    print("Active Network: ")
    print(network.show_active() + "\n")

    # Deploying contracts
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplace.deploy({'from': accounts[0]})
    #proxy = EmogramsMarketplaceProxy.deploy()

    # Miki, Csongor, Patr, Adr
    founders = [MIKI, CSONGOR, PATR, ADR]
    founders_pct = [50, 5, 22.5, 22.5]
    founders_pct = [x*10000 for x in founders_pct]
    vault = FounderVault.deploy(founders, founders_pct, {'from': accounts[0]})
    
    print("Contracts deployed\n")

    # Minting Emogram NFT tokens
    mint_token_ids = list(range(2, 101))
    mint_amounts = [1 for i in range(99)]
    emograms.mintBatch(accounts[0], mint_token_ids, mint_amounts, "")

