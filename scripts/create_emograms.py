from brownie import Emogramscollectible, accounts, network, config


def main():
    #get the wallets from the dev network, print active network

    dev = accounts.add(config["wallets"]["from_key"])
    print(network.show_active())

    