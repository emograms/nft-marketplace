import time
import random
from os import initgroups
from brownie import EmogramsCollectible, EmogramMarketplace, EmogramsMarketplaceProxy, accounts


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

def test_fixed_buy_cancel():
    '''
    Testing the fixed price selling mechanism cancel function
    '''

def test_fixed_buy():
    '''
    Minting an NFT, approving marketplace, selling on fixed price and buying
    Reselling the bought NFT and checking royalty amounts
    '''
    
    seller_init_balance = accounts[0].balance()
    seller_init_balance_1 = accounts[1].balance()
    sell_price = 1e18
    royalty_pct = 0.075
    buyer_init_balance = accounts[2].balance()
    token_id_2 = 2
    token_id_3 = 3
    
    # Try buying own emogram
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplace.deploy(True, {'from': accounts[0]})
    emograms.createEmogram({'from': accounts[0]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[0]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[1]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[2]})
    tx_sell = marketplace.addEmogramToMarket(token_id_2, emograms, sell_price, {'from': accounts[0]})
    try: 
        marketplace.buyEmogram(0, {'from': accounts[0], 'amount': sell_price})
    except Exception as e:
        assert 'Cannot buy own item' in e.revert_msg

    assert tx_sell.events['EmogramAdded']['id'] == tx_sell.return_value
    assert tx_sell.events['EmogramAdded']['tokenId'] == token_id_2
    assert tx_sell.events['EmogramAdded']['tokenAddress'] == emograms
    assert tx_sell.events['EmogramAdded']['askingPrice'] == sell_price
    assert emograms.balanceOf(accounts[0], 2, {'from': accounts[0]}) == 1
    assert accounts[0].balance() == seller_init_balance

    # Buying others emogram and Royalty checks
    emograms.createEmogram({'from': accounts[0]})
    emograms.safeTransferFrom(accounts[0], accounts[1], 3, 1, '')
    marketplace.addEmogramToMarket(token_id_3, emograms, sell_price, {'from': accounts[1]})
    tx_buy = marketplace.buyEmogram(tx_sell.return_value+1, {'from': accounts[2], 'amount': sell_price})

    # Event checks
    assert tx_buy.events['EmogramSold']['id'] == tx_sell.return_value+1
    assert tx_buy.events['EmogramSold']['tokenId'] == token_id_3
    assert tx_buy.events['EmogramSold']['buyer'] == accounts[2]
    assert tx_buy.events['EmogramSold']['askingPrice'] == sell_price

    # Token balance checks
    assert emograms.balanceOf(accounts[0], 3, {'from': accounts[0]}) == 0
    assert emograms.balanceOf(accounts[1], 3, {'from': accounts[0]}) == 0
    assert emograms.balanceOf(accounts[2], 3, {'from': accounts[0]}) == 1

    # ETH balance checks
    assert accounts[1].balance() == seller_init_balance_1 + sell_price - (sell_price*royalty_pct)
    assert accounts[2].balance() == buyer_init_balance - sell_price



def test_auction_cancel():
    '''
    Minting an NFT, approving marketplace, selling on auction and canceling it
    '''
    token_id = 2
    duration = 5
    start_price = 1e18
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplace.deploy(True, {'from': accounts[0]})
    emograms.createEmogram({'from': accounts[0]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[0]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[1]})
    timestamp = round(time.time())
    tx_create = marketplace.createAuction(token_id, emograms, duration, start_price, {'from': accounts[0]})
    assert marketplace.emogramsOnAuction(0)['onAuction'] == True
    assert tx_create.events['AuctionCreated']['id'] == tx_create.return_value
    assert tx_create.events['AuctionCreated']['tokenId'] == token_id
    assert tx_create.events['AuctionCreated']['seller'] == accounts[0]
    assert tx_create.events['AuctionCreated']['tokenAddress'] == emograms
    assert tx_create.events['AuctionCreated']['startPrice'] == start_price
    assert (tx_create.events['AuctionCreated']['duration'] == timestamp+duration) or (tx_create.events['AuctionCreated']['duration'] == timestamp+duration-1) or (tx_create.events['AuctionCreated']['duration'] == timestamp+duration+1)
    # Testing a cancel from another account
    try: 
        marketplace.cancelAuction(0, 2, emograms, {'from': accounts[1]})
    except Exception as e:
        assert 'Not owner' in e.revert_msg
        assert marketplace.emogramsOnAuction(0)['onAuction'] == True
    
    # Testing cancel from own account
    tx_cancel = marketplace.cancelAuction(0, 2, emograms, {'from': accounts[0]})
    assert marketplace.emogramsOnAuction(0)['onAuction'] == False
    assert tx_cancel.events['AuctionCanceled']['id'] == tx_create.return_value
    assert tx_cancel.events['AuctionCanceled']['tokenId'] == token_id
    assert tx_cancel.events['AuctionCanceled']['seller'] == accounts[0]
    assert tx_cancel.events['AuctionCanceled']['tokenAddress'] == emograms


def test_auction_buy_finish():
    '''
    Minting an NFT, approving marketplace, selling on auction price and buying
    
    todo:
    - auction lower than sell price
    - auction higher than sell price, but lower than highest bid
    
    '''
    auction_time = 5
    royalty_pct = 0.075
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

    # Transfer emogram[2] to account[1]
    emograms.safeTransferFrom(accounts[0], accounts[1], 2, 1, '')
    # Create auctions
    # account[0] - 1,3
    # account[1] - 0,2
    marketplace.createAuction(2, emograms, auction_time, sell_price, {'from': accounts[1]})
    marketplace.createAuction(3, emograms, auction_time, sell_price, {'from': accounts[0]})

    # Place 2 bids from different accounts
    marketplace.PlaceBid(0, 2, emograms, {'from': accounts[2], 'value': bid_price_1})
    marketplace.PlaceBid(0, 2, emograms, {'from': accounts[3], 'value': bid_price_2})
    auction = marketplace.emogramsOnAuction(0)
    print('auctionItem[0]: ', auction)
    
    # Check if the auction can be finished before endDate
    try: 
        marketplace.finishAuction(emograms, 3, 1, {'from': accounts[0]})
    except Exception as e:
        assert 'Auction is still ongoing' in e.revert_msg
    
    # Wait for endDate and finish auctions
    time.sleep(auction_time+1)
    marketplace.finishAuction(emograms, 2, 0, {'from': accounts[1]})
    tx_finish = marketplace.finishAuction(emograms, 3, 1, {'from': accounts[0]})
    
    # Token balance checks
    assert emograms.balanceOf(accounts[0], 2, {'from': accounts[0]}) == 0
    assert emograms.balanceOf(accounts[1], 2, {'from': accounts[0]}) == 0
    assert emograms.balanceOf(accounts[2], 2, {'from': accounts[0]}) == 0
    assert emograms.balanceOf(accounts[3], 2, {'from': accounts[0]}) == 1

    # ETH balance checks
    assert accounts[0].balance() == seller_init_balance_1 + bid_price_2*royalty_pct
    assert accounts[1].balance() == seller_init_balance_2 + bid_price_2 - bid_price_2*royalty_pct
    assert accounts[2].balance() == buyer_init_balance_1
    assert accounts[3].balance() == buyer_init_balance_2 - bid_price_2

    # Event checks
    assert tx_finish.events['AuctionFinished']['id'] == tx_finish.return_value
    assert tx_finish.events['AuctionFinished']['tokenId'] == 3
    assert tx_finish.events['AuctionFinished']['highestBidder'] == accounts[0]
    assert tx_finish.events['AuctionFinished']['seller'] == accounts[0]
    assert tx_finish.events['AuctionFinished']['highestBid'] == 1000000000000000000


    #event AuctionFinished(uint256 indexed id, uint256 indexed tokenId, address indexed highestBidder, address seller, uint256 highestBid);

def test_initial_auction():
    '''
    Testing initial auction by minting all emograms with batchMint, 
    putting up 3 for initial auction, bid for 2, leave 1 unbidded and finish auction.
    Retest by launching a new daily auction with stepAuction fn.
    '''
    auction_time = 3
    seller_init_balance = accounts[0].balance()
    buyer_init_balance_1 = accounts[1].balance()
    buyer_init_balance_2 = accounts[2].balance()
    buyer_init_balance_3 = accounts[3].balance()
    bid_price_1 = 1.1e18
    bid_price_2 = 1.2e18

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

    for idx, price in enumerate(initial_auction_prices):        
        print('Auction cycle #%s' %(idx))
        step_auction = marketplace.stepAuctions(emograms, price, auction_time)
        for i in range(3*idx,3*idx+3):
            print('Emogram id #%s' %(i))
            # Do checks
            tx = marketplace.emogramsOnAuction(i)
            assert tx['onAuction'] == True
            assert tx['tokenId'] == initial_order[i]
            assert tx['startPrice'] == price
        
        # Bid for only every 3
        if i%3==0:
            marketplace.PlaceBid(i, tx['tokenId'], emograms, {'from': accounts[2], 'value': bid_price_1})
            marketplace.PlaceBid(i, tx['tokenId'], emograms, {'from': accounts[3], 'value': bid_price_2})

        # Check if every third is owned by accounts[3] and the rest is owned by accounts[0]
        if idx > 0:
            if i%3==0:
                assert emograms.balanceOf(accounts[0], initial_order[idx], {'from': accounts[0]}) == 0
                assert emograms.balanceOf(accounts[2], initial_order[idx], {'from': accounts[0]}) == 0
                assert emograms.balanceOf(accounts[3], initial_order[idx], {'from': accounts[0]}) == 1
            else:
                assert emograms.balanceOf(accounts[0], initial_order[idx], {'from': accounts[0]}) == 1
                assert emograms.balanceOf(accounts[2], initial_order[idx], {'from': accounts[0]}) == 0
                assert emograms.balanceOf(accounts[3], initial_order[idx], {'from': accounts[0]}) == 0

    # Check if initialAuction period ended
    assert 'InitialAuctionFinished' in step_auction.events

def test_proxy():
    '''
    Deploying contracts with proxy scheme and testing upgradability
    '''
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplace.deploy(True, {'from': accounts[0]})
    proxy = EmogramsMarketplaceProxy.deploy(accounts[0], marketplace, {'from': accounts[0]})
    #assert '' in tx.events
    #proxy.upgradeTo(marketplace.address)
    #assert proxy. == marketplace.address

'''
Todo:
- cancel fix price buy
- proxy implementation and upgradability checks
- initialAuctionFinished event
- event checks in all function
'''