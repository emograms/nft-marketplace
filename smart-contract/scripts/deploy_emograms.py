import os, time
from brownie import EmogramsCollectible, EmogramMarketplace, accounts, network


def main():
    dev = accounts.load(0)
    print("Active Network: ")
    print(network.show_active() + "\n")
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplace.deploy({'from': accounts[0]})

    print("Contracts deployed\n")
    
    #emograms.createEmogramsCollection(99, {'from': accounts[0]})
    print(len(list(range(2,101))))
    print([1 for i in range(99)])
    print(len([1 for i in range(99)]))
    emograms.mintBatch(accounts[0], list(range(2,101)), [1 for i in range(99)], "")
    
    y = 0
    for x in range(0,101):
        if(emograms.balanceOf(accounts[0], x, {'from': accounts[0]}) != 0):
            y = y + emograms.balanceOf(accounts[0], x, {'from': accounts[0]})
    print("Total emograms minted: ")
    print(y)

    emograms.createFunToken(110, 1, {'from': accounts[0]})
    print(emograms.balanceOf(accounts[0], 1, {'from': accounts[0]}))

    emograms.setApprovalForAll(marketplace, True, {'from': accounts[0]})

    marketplace.addEmogramToMarket(2, emograms, 10, {'from': accounts[0]})
    marketplace.buyEmogram(0, {'from': accounts[1], 'amount': 10000000000000000000})
    print(emograms.balanceOf(accounts[1], 2, {'from': accounts[0]}))

    print("Sell succesfull")

    print("creating auction")

    marketplace.createAuction(3, emograms, 10, 10000000000000000000, {'from': accounts[0]})
    
    print("Placing Bid")
    marketplace.PlaceBid(0, 3, emograms, {'from': accounts[1], 'amount': 11000000000000000000})

    print(marketplace.getBalance({'from': accounts[0]}))

    time.sleep(2)

    marketplace.cancelAuction(0, 3, emograms)

    marketplace.createAuction(4, emograms, 10, 10000000000000000000, {'from': accounts[0]})

    marketplace.createAuction(5, emograms, 10, 10000000000000000000, {'from': accounts[0]})

    marketplace.PlaceBid(2, 5, emograms, {'from': accounts[1], 'amount': 11000000000000000000})

    time.sleep(11)

    marketplace.finishAuction(emograms, 4, 1, {'from': accounts[0]})
    marketplace.finishAuction(emograms, 4, 2, {'from': accounts[0]})




    