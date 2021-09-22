import time
import random
from os import initgroups
from brownie import EmogramsCollectible, EmogramMarketplaceUpgradeable, FounderVault, ERC1967Proxy, accounts
import eth_utils


"""
TODO

"""
def encode_function_data(initializer=None, *args):
    """Encodes the function call so we can work with an initializer.
    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
        The initializer function we want to call. Example: `box.store`.
        Defaults to None.
        args (Any, optional):
        The arguments to pass to the initializer function
    Returns:
        [bytes]: Return the encoded bytes.
    """
    if len(args) == 0 or not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    else:
        return initializer.encode_input(*args)

def main():
    dev = accounts.load(0)
    print("Active Network: ")
    print(network.show_active() + "\n")
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplaceUpgradeable.deploy({'from': accounts[0]})
    marketplace_encoded_init_function = encode_function_data(initializer=marketplace.initialize(True))
    proxy = ERC1967Proxy.deploy(marketplace, marketplace_encoded_init_function, {'from': accounts[0]})
    foundervault = FounderVault.deploy(accounts[0:5], [20, 20, 30, 15, 15], {'from': accounts[0]})

    print("Contracts deployed\n")

    emograms.setBeneficiary(foundervault, {'from': accounts[0]})
    print("FounderVault set as royalty beneficiary")
    #emograms.createEmogramsCollection(99, {'from': accounts[0]})
    """   print(len(list(range(2, 101))))
    print([1 for i in range(99)])
    print(len([1 for i in range(99)])) """

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

    emograms.setApprovalForAll(proxy, True, {'from': accounts[0]})

    proxy.addEmogramToMarket(2, emograms, 1e18, {'from': accounts[0]})
    proxy.buyEmogram(
        0, {'from': accounts[1], 'amount': 1e18})
    print(emograms.balanceOf(accounts[1], 2, {'from': accounts[0]}))
    print("Sell succesfull")

    print('----Auction create & Cancel w/o bid----')
    print("Creating auction eid#3")
    proxy.createAuction(
        3, emograms, 10, 1e18, {'from': accounts[0]})
    print("Placing Bid eid#3")
    proxy.PlaceBid(
        0, 3, emograms, {'from': accounts[1], 'amount': 1.1e18})
    time.sleep(2)
    print("Canceling auction eid#3")
    proxy.cancelAuction(0, 3, emograms)

    print('----Auction create & finish w/o bid----')
    print("Creating auction eid#4")
    proxy.createAuction(
        4, emograms, 10, 1e18, {'from': accounts[0]})
    print("Finishing auction eid#4")
    time.sleep(11)
    proxy.finishAuction(emograms, 4, 1, {'from': accounts[0]})

    print("FounderVault Balance: ", foundervault.balance())


    print('----Auction create & finish w/ bid----')
    print("Creating auction eid#5")
    proxy.createAuction(
        5, emograms, 10, 1e18, {'from': accounts[0]})
    print("Placing Bid eid#5")
    proxy.PlaceBid(
        2, 5, emograms, {'from': accounts[1], 'amount': 1.1e18})
    time.sleep(11)
    print('mktplace balance: ', proxy.balance()/1e18)
    for key in proxy.emogramsOnAuction(2).keys():
        print(key, ':', proxy.emogramsOnAuction(2)[key])
    print("Finishing auction eid#5")
    proxy.finishAuction(emograms, 5, 2, {'from': accounts[0]})

    print("FounderVault Balance: ", foundervault.balance())

    emograms.setURI("https://gateway.pinata.cloud/ipfs/QmQhJB3Ep5sfjaAArr5mhJeXMcycNHeJQv8qVfkaSDaHeW/{id}.json", {'from': accounts[0]})
    print(emograms.uri(3, {'from': accounts[0]}))



