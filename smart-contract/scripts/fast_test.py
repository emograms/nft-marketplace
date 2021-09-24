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


import eth_utils

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

emograms = EmogramsCollectible.deploy({'from': accounts[0]})
marketplace = EmogramMarketplaceUpgradeable.deploy({'from': accounts[0]})
marketplace_encoded_init_function = encode_function_data(True)
proxy = ERC1967Proxy.deploy(marketplace, marketplace_encoded_init_function, {'from': accounts[0]})
proxy_abi = Contract.from_abi("EmogramMarketplaceUpgradeable", proxy.address, EmogramMarketplaceUpgradeable.abi)
proxy_abi.initialize(True, {'from': accounts[0]})
emograms.createEmogram({'from': accounts[0]})
emograms.setApprovalForAll(proxy_abi, True, {'from': accounts[0]})
proxy_abi.addEmogramToMarket(2, emograms, 1e18, {'from': accounts[0]})
print(proxy_abi.emogramsOnSale(0))

assert proxy_abi.emogramsOnSaleLength() == 1

marketplace_v2 = EmogramMarketplaceUpgradeable_UpgradeTest.deploy({'from': accounts[0]})
proxy_abi.upgradeTo(marketplace_v2, {'from': accounts[0]})
proxy_abi_v2 = Contract.from_abi("EmogramMarketplaceUpgradeable_UpgradeTest", proxy.address, EmogramMarketplaceUpgradeable_UpgradeTest.abi)

assert proxy_abi_v2.emogramsOnSaleLength() == 2
newfunction = proxy_abi_v2.newFunction()
assert newfunction == 'Upgraded'