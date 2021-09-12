import time
from brownie import EmogramsCollectible, EmogramMarketplace, accounts


def test_deploy():
    '''
    Deployment steps with assertion of contract roles
    '''
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplace.deploy({'from': accounts[0]})

    def assert_contract_roles(contract, role_list, account):
        '''
        Check if a given contract is able to access specific roles from a list
        '''
        emograms_assert_list = []
        for role in role_list:
            emograms_assert_list.append(
                contract.hasRole(role, account.address))
        assert False not in emograms_assert_list

    # Checking nft and marketplace contracts and its roles if the deployer address has these roles

    nft_role_hash_list = [
        emograms.BENEFICIARY_UPGRADER_ROLE(),
        emograms.DEFAULT_ADMIN_ROLE(),
        emograms.MINTER_ROLE(),
        emograms.URI_SETTER_ROLE()]

    assert_contract_roles(emograms, nft_role_hash_list, accounts[0])

    marketplace_role_hash_list = [
        marketplace.DEFAULT_ADMIN_ROLE(),
        marketplace.FOUNDER_ROLE()]

    assert_contract_roles(marketplace, marketplace_role_hash_list, accounts[0])

    # Check if base percentage is 7.5% (uint 750)
    assert emograms.BASE_PERCENTAGE() == 750


def test_check_balances_nft_srt():
    '''
    Check NFT and SRT balances on the contract, which should be zero after deployment
    '''
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})

    # Check SRT (1), NFT(2-100) balance, should be zero
    for i in range(1, 100):
        assert emograms.balanceOf(accounts[0], i, {'from': accounts[0]}) == 0


def test_minting():
    '''
    Minting 99 pcs. of NFT tokens with the specific roles and others as well
    '''
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})

    # Minting SRT and NFT 1-1
    emograms.createFunToken(1, 1, {'from': accounts[0]})

    for i in range(0, 10):
        emograms.createEmogram({'from': accounts[0]})

    # Check SRT (1), NFT(2-100) balance, should be 1
    for i in range(1, 12):
        assert emograms.balanceOf(accounts[0], i, {'from': accounts[0]}) == 1


def test_fixed_buy():
    '''
    Minting an NFT, approving marketplace, selling on fixed price and buying
    '''
    seller_init_balance = accounts[0].balance()
    sell_price = 1e8
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplace.deploy({'from': accounts[0]})
    emograms.createEmogram({'from': accounts[0]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[0]})
    marketplace.addEmogramToMarket(
        2, emograms, sell_price, {'from': accounts[0]})
    marketplace.buyEmogram(
        0, {'from': accounts[1], 'amount': 10000000000000000000})

    assert emograms.balanceOf(accounts[1], 2, {'from': accounts[0]}) == 1
    assert accounts[0].balance() == seller_init_balance + sell_price


def test_auction_cancel():
    '''
    Minting an NFT, approving marketplace, selling on auction and canceling it
    '''

    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplace.deploy({'from': accounts[0]})
    emograms.createEmogram({'from': accounts[0]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[0]})
    marketplace.createAuction(2, emograms, 10, 1e18, {'from': accounts[0]})
    marketplace.cancelAuction(0, 2, emograms, {'from': accounts[0]})


def test_auction_buy():
    '''
    Minting an NFT, approving marketplace, selling on auction price and buying
    '''

    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplace.deploy({'from': accounts[0]})
    emograms.createEmogram({'from': accounts[0]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[0]})
    # Approval already needed for Bidding of account[1]
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[1]})
    marketplace.createAuction(2, emograms, 10, 1e18, {'from': accounts[0]})
    marketplace.PlaceBid(
        0, 2, emograms, {'from': accounts[1], 'value': 0.123e18})
    auction = marketplace.emogramsOnAuction(0)
    print('auctionItem[0]: ', auction)
    marketplace.finishAuction(emograms, 2, 0, {'from': accounts[0]})


'''
Todo:
- auction finish without bid
- auction finish with bid
- mint 6 emograms, put up 3 for initial auction, bid for 2 and leave 1 unbidded, call stepAuction to close and repeate
'''


auction_time = 15
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
