import time
import random
from os import initgroups
from brownie import EmogramsCollectible, EmogramMarketplace, accounts


def test_deploy():
    '''
    Deployment steps with assertion of contract roles
    '''
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplace.deploy(True, {'from': accounts[0]})

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
    sell_price = 1e18
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplace.deploy(True, {'from': accounts[0]})
    emograms.createEmogram({'from': accounts[0]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[0]})
    marketplace.addEmogramToMarket(
        2, emograms, sell_price, {'from': accounts[0]})
    marketplace.buyEmogram(
        0, {'from': accounts[1], 'amount': sell_price})

    assert emograms.balanceOf(accounts[1], 2, {'from': accounts[0]}) == 1
    assert accounts[0].balance() == seller_init_balance + sell_price


def test_auction_cancel():
    '''
    Minting an NFT, approving marketplace, selling on auction and canceling it
    '''

    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplace.deploy(True, {'from': accounts[0]})
    emograms.createEmogram({'from': accounts[0]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[0]})
    marketplace.createAuction(2, emograms, 10, 1e18, {'from': accounts[0]})
    assert marketplace.emogramsOnAuction(0)['onAuction'] == True
    marketplace.cancelAuction(0, 2, emograms, {'from': accounts[0]})
    assert marketplace.emogramsOnAuction(0)['onAuction'] == False


def test_auction_buy_finish():
    '''
    Minting an NFT, approving marketplace, selling on auction price and buying
    
    todo:
    - auction lower than sell price
    - auction higher than sell price, but lower than highest bid
    
    '''
    auction_time = 5
    seller_init_balance_1 = accounts[0].balance()
    seller_init_balance_2 = accounts[1].balance()
    buyer_init_balance_1 = accounts[2].balance()
    buyer_init_balance_2 = accounts[3].balance()
    sell_price = 1e18
    bid_price_1 = 1.1e18
    bid_price_2 = 1.2e18

    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplace.deploy(True, {'from': accounts[0]})
    emograms.createEmogram({'from': accounts[0]})
    emograms.createEmogram({'from': accounts[0]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[0]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[1]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[2]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[3]})

    # Transfer emograms to account[1] for free
    marketplace.addEmogramToMarket(
        2, emograms, 0, {'from': accounts[0]})
    marketplace.buyEmogram(
        0, {'from': accounts[1], 'amount': 0})  
    
    # Create auctions
    # account[0] - 1,3
    # account[1] - 0,2
    marketplace.createAuction(2, emograms, auction_time, sell_price, {'from': accounts[1]})
    marketplace.createAuction(3, emograms, auction_time, sell_price, {'from': accounts[0]})

    # Place 2 bids from different accounts
    marketplace.PlaceBid(
        0, 2, emograms, {'from': accounts[2], 'value': bid_price_1})
    marketplace.PlaceBid(
        0, 2, emograms, {'from': accounts[3], 'value': bid_price_2})
    auction = marketplace.emogramsOnAuction(0)
    print('auctionItem[0]: ', auction)
    
    # Check if the auction can be finished before endDate
    try: 
        marketplace.finishAuction(emograms, 3, 1, {'from': accounts[0]})
    except Exception as e:
        assert 'Auction is still ongoing.' == e.revert_msg
    
    # Wait for endDate and finish auctions
    time.sleep(auction_time+1)
    marketplace.finishAuction(emograms, 2, 0, {'from': accounts[1]})
    marketplace.finishAuction(emograms, 3, 0, {'from': accounts[0]})
    
    assert emograms.balanceOf(accounts[0], 2, {'from': accounts[0]}) == 0
    assert emograms.balanceOf(accounts[1], 2, {'from': accounts[0]}) == 0
    assert emograms.balanceOf(accounts[2], 2, {'from': accounts[0]}) == 0
    assert emograms.balanceOf(accounts[3], 2, {'from': accounts[0]}) == 1

    print('mktplace balance: ', marketplace.balance()/1e18)

    assert accounts[0].balance() == seller_init_balance_1
    assert accounts[1].balance() == seller_init_balance_2 + bid_price_2
    assert accounts[2].balance() == buyer_init_balance_1
    assert accounts[3].balance() == buyer_init_balance_2 - bid_price_2

def test_initial_auction():
    '''
    Testing initial auction by minting all emograms with batchMint, 
    putting up 3 for initial auction, bid for 2, leave 1 unbidded and finish auction.
    Retest by launching a new daily auction with stepAuction fn.
    '''
    auction_time = 5
    seller_init_balance = accounts[0].balance()
    buyer_init_balance_1 = accounts[1].balance()
    buyer_init_balance_2 = accounts[2].balance()
    buyer_init_balance_3 = accounts[3].balance()
    bid_price = 1.1e18

    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplace.deploy(True, {'from': accounts[0]})
    
    initial_auction_prices = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    for i in range(0, 33-len(initial_auction_prices)):
        initial_auction_prices.append(1.0)
    assert len(initial_auction_prices) == 33
    
    initial_order = [x for x in range(2,101)]
    random.shuffle(initial_order)
    assert len(initial_order) == 99
    marketplace.setInitialorder(initial_order)
    
    emograms.mintBatch(accounts[0], list(range(2, 101)), [1 for i in range(99)], "")
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[0]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[1]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[2]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[3]})

    #for day in initial_auction_prices:
        

       

    
    
'''
Todo:
- mint all emograms, put up 3 for initial auction, bid for 2 and leave 1 unbidded, call stepAuction to close and repeate 
'''