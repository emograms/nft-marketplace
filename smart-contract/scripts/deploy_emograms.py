import os
from brownie import EmogramsCollectible, EmogramMarketplace, accounts, network, config


def main():
    dev = accounts.load(0)
    print("Active Network: ")
    print(network.show_active() + "\n")
    print("Active address in use: " + dev)
    emograms = EmogramsCollectible.deploy({'from': dev})
    marketplace = EmogramMarketplace.deploy({'from': dev})

    print("Contracts deployed")
