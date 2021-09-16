import os
import time
from brownie import EmogramsCollectible, EmogramMarketplace, FounderVault, accounts, network

def main():
    dev = accounts.load(0)
    print("Active Network: ")
    print(network.show_active() + "\n")
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplace.deploy(True, {'from': accounts[0]})
    foundervault = FounderVault.deploy(accounts[0:5], [20, 20, 30, 15, 15], {'from': accounts[0]}) #Testing accounts so far

    print("Contracts deployed\n")

    emograms.setBeneficiary(foundervault, {'from': accounts[0]})
    print("FounderVault set as royalty beneficiary")

    emograms.mintBatch(accounts[0], list(range(2, 101)), [
                       1 for i in range(99)], "")

    y = 0
    for x in range(0, 101):
        if(emograms.balanceOf(accounts[0], x, {'from': accounts[0]}) != 0):
            y = y + emograms.balanceOf(accounts[0], x, {'from': accounts[0]})
    print("Total emograms minted: ")
    print(y)

    emograms.createFunToken(110, 1, {'from': accounts[0]})
    print(emograms.balanceOf(accounts[0], 1, {'from': accounts[0]}))

    emograms.setApprovalForAll(marketplace, True, {'from': accounts[0]})

    emograms.setURI("https://gateway.pinata.cloud/ipfs/QmQhJB3Ep5sfjaAArr5mhJeXMcycNHeJQv8qVfkaSDaHeW/{id}.json", {'from': accounts[0]})
    print(emograms.uri(2, {'from': accounts[0]}))


