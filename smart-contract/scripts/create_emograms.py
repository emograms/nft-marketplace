from brownie import Emogramscollectible, accounts, network, config


def main():
    
    dev = accounts.add(config["wallets"]["from_key"])
    print(network.show_active())