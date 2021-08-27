import os
from brownie import EmogramsCollectible, EmogramMarketplace, accounts, network, config


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