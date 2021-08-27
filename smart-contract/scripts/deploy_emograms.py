import os
from brownie import EmogramsCollectible, EmogramMarketplace, accounts, network


def main():
    dev = accounts.load(0)
    print("Active Network: ")
    print(network.show_active() + "\n")
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplace.deploy({'from': accounts[0]})

    print("Contracts deployed\n")

    for x in range(0,9):
        print("Minting Emogram\n")
        emograms.createEmogram({'from': accounts[0]})
        print(emograms.balanceOf(accounts[0], x, {'from': accounts[0]}))

    y = 0
    for x in range(0,100):
        if(emograms.balanceOf(accounts[0], x, {'from': accounts[0]}) != 0):
            y = y + emograms.balanceOf(accounts[0], x, {'from': accounts[0]})
    print("Total emograms minted: ")
    print(y)

    emograms.createFunToken(2970, 1, {'from': accounts[0]})
    print(emograms.balanceOf(accounts[0], 1, {'from': accounts[0]}))

    emograms.setApprovalForAll(marketplace, True, {'from': accounts[0]})

    marketplace.addEmogramToMarket(2, emograms, 10, {'from': accounts[0]})
    marketplace.buyEmogram(0, {'from': accounts[1], 'amount': 10000000000000000000})
    print(emograms.balanceOf(accounts[1], 2, {'from': accounts[0]}))