import time
from brownie import EmogramsCollectible, EmogramMarketplace, FounderVault, accounts, network

auction_time = 15
dev = accounts.load(0)
print(accounts[0].balance())

emograms = EmogramsCollectible.deploy({'from': accounts[0]})
marketplace = EmogramMarketplace.deploy({'from': accounts[0]})
emograms.createEmogram({'from': accounts[0]})
emograms.setApprovalForAll(marketplace, True, {'from': accounts[0]})
emograms.setApprovalForAll(marketplace, True, {'from': accounts[1]})
emograms.setApprovalForAll(marketplace, True, {'from': accounts[2]})


marketplace.createAuction(2, emograms, auction_time,
                          1e18, {'from': accounts[0]})
marketplace.PlaceBid(
    0, 2, emograms, {'from': accounts[1], 'value': 1.23e18})
marketplace.PlaceBid(
    0, 2, emograms, {'from': accounts[2], 'value': 1.24e18})

auction = marketplace.emogramsOnAuction(0)
print('auctionItem[0]: ', auction)

print('SLEEP: ', auction_time, 'sec')
time.sleep(auction_time+1)
tx2 = marketplace.finishAuction(emograms, 2, 0, {'from': accounts[2]})
auction = marketplace.emogramsOnAuction(0)
print('auctionItem[0]: ', auction)
print(accounts[0].balance())


emograms = EmogramsCollectible.deploy({'from': accounts[0]})
marketplace = EmogramMarketplace.deploy({'from': accounts[0]})
emograms.createEmogram({'from': accounts[0]})
emograms.setApprovalForAll(marketplace, True, {'from': accounts[0]})
marketplace.createAuction(2, emograms, 30, 1e18, {'from': accounts[0]})
tx = marketplace.cancelAuction(0, 2, emograms, {'from': accounts[0]})
