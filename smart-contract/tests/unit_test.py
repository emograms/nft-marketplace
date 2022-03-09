import time
import random
from os import initgroups
import eth_utils
from brownie import *
import uuid, hashlib
from hexbytes import HexBytes

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


def test_deploy():
    '''
    Deployment steps with assertion of contract roles
    '''
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplaceUpgradeable.deploy({'from': accounts[0]})
    SRToken = SculptureRedemptionToken.deploy({'from': accounts[0]})
    marketplace.initialize(True, {'from': accounts[0]})

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
    # assert emograms.BASE_PERCENTAGE() == 750

def test_name_symbol():
    '''
    Test deployed name and symbol
    '''
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    assert emograms.symbol() == 'EGRAMS'
    assert emograms.name() == 'Emograms'


def test_check_balances_nft_srt():
    '''
    Check NFT and SRT balances on the contract, which should be zero after deployment
    '''
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})

    # Check SRT (1), NFT(2-100) balance, should be zero
    for i in range(1, 100):
        assert emograms.balanceOf(accounts[0], i, {'from': accounts[0]}) == 0

def test_ownerOf_ownerOfById():
    '''
    Testing ownerOf and ownerOfById functions
    '''
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    assert emograms.ownerOf(2, accounts[0]) == False
    assert emograms.ownerOfById(2) == '0x0000000000000000000000000000000000000000'
    
    emograms.createEmogram({'from': accounts[0]})
    assert emograms.ownerOf(2, accounts[0]) == True
    assert emograms.ownerOf(2, accounts[1]) == False
    assert emograms.ownerOf(1, accounts[1]) == False
    assert emograms.ownerOf(1, accounts[0]) == False
    assert emograms.ownerOfById(2) == accounts[0]
    
    emograms.createFunToken(1, 1, {'from': accounts[0]})
    assert emograms.ownerOf(1, accounts[0]) == True
    assert emograms.ownerOfById(1) == accounts[0]

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
    seller_init_balance = accounts[0].balance()
    sell_price = 1e18
    token_id_2 = 2
    # Try canceling fix price 
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplaceUpgradeable.deploy({'from': accounts[0]})
    marketplace.initialize(True, {'from': accounts[0]})
    emograms.createEmogram({'from': accounts[0]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[0]})
    tx_sell = marketplace.addEmogramToMarket(token_id_2, emograms, sell_price, {'from': accounts[0]})
    sell_id = tx_sell.return_value
    sell_item = marketplace.emogramsOnSale(sell_id)

    # Assert emitted EmogramAdded event
    assert tx_sell.events['EmogramAdded']['id'] == sell_id
    assert tx_sell.events['EmogramAdded']['tokenId'] == token_id_2
    assert tx_sell.events['EmogramAdded']['tokenAddress'] == emograms.address
    assert tx_sell.events['EmogramAdded']['askingPrice'] == sell_price

    # Assert emogramsOnSale array[0]
    assert sell_item['sellId'] == sell_id
    assert sell_item['tokenAddress'] == emograms.address
    assert sell_item['tokenId'] == token_id_2
    assert sell_item['seller'] == accounts[0]
    assert sell_item['price'] == sell_price
    assert sell_item['isSold'] == False

    # Assert activeEmograms
    assert marketplace.activeEmograms(emograms, 2) == True

    # Cancel sell
    tx_cancel = marketplace.cancelSell(sell_id)
    canceled_sell_item = marketplace.emogramsOnSale(sell_id)

    # Assert cancel events
    assert tx_cancel.events['SellCancelled']['sender'] == accounts[0]
    assert tx_cancel.events['SellCancelled']['tokenId'] == token_id_2
    assert tx_cancel.events['SellCancelled']['tokenAddress'] == emograms.address

    # Assert emogramsOnSale array[0]
    assert canceled_sell_item['sellId'] == sell_id
    assert canceled_sell_item['tokenAddress'] == '0x0000000000000000000000000000000000000000'
    assert canceled_sell_item['tokenId'] == 0
    assert canceled_sell_item['seller'] == '0x0000000000000000000000000000000000000000'
    assert canceled_sell_item['price'] == 0
    assert canceled_sell_item['isSold'] == False

    # Assert activeEmograms
    assert marketplace.activeEmograms(emograms, 2) == False

    # Assert increased emogramsOnSale id
    tx_sell = marketplace.addEmogramToMarket(token_id_2, emograms, sell_price, {'from': accounts[0]})
    assert sell_id+1 == tx_sell.return_value

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
    marketplace = EmogramMarketplaceUpgradeable.deploy({'from': accounts[0]})
    marketplace.initialize(True, {'from': accounts[0]})
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
    marketplace = EmogramMarketplaceUpgradeable.deploy({'from': accounts[0]})
    marketplace.initialize(True, {'from': accounts[0]})
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
    marketplace = EmogramMarketplaceUpgradeable.deploy({'from': accounts[0]})
    marketplace.initialize(True, {'from': accounts[0]})
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
    current_time = int(time.time())
    tx_auction_2 = marketplace.createAuction(2, emograms, auction_time, sell_price, {'from': accounts[1]})
    tx_auction_3 = marketplace.createAuction(3, emograms, auction_time, sell_price, {'from': accounts[0]})

    auction_2_0 = marketplace.emogramsOnAuction(tx_auction_2.return_value)
    auction_3_0 = marketplace.emogramsOnAuction(tx_auction_3.return_value)

    assert auction_2_0['auctionId'] == tx_auction_2.return_value
    assert auction_2_0['tokenAddress'] == emograms
    assert auction_2_0['tokenId'] == 2
    assert auction_2_0['seller'] == accounts[1]
    assert auction_2_0['highestBidder'] == accounts[1]
    assert auction_2_0['startPrice'] == sell_price
    assert auction_2_0['highestBid'] == sell_price
    assert auction_2_0['endDate'] == current_time + auction_time
    assert auction_2_0['onAuction'] == True

    # Place 2 bids from different accounts
    tx_bid_2_0 = marketplace.PlaceBid(0, 2, emograms, {'from': accounts[2], 'value': bid_price_1})
    auction_2_0 = marketplace.emogramsOnAuction(tx_bid_2_0.return_value)
    tx_bid_2_1 = marketplace.PlaceBid(0, 2, emograms, {'from': accounts[3], 'value': bid_price_2})
    auction_2_1 = marketplace.emogramsOnAuction(tx_bid_2_1.return_value)

    # Asserting emogramsOnAuction
    assert auction_2_0['auctionId'] == tx_bid_2_0.return_value
    assert auction_2_0['tokenAddress'] == emograms
    assert auction_2_0['tokenId'] == 2
    assert auction_2_0['seller'] == accounts[1]
    assert auction_2_0['highestBidder'] == accounts[2]
    assert auction_2_0['startPrice'] == sell_price
    assert auction_2_0['highestBid'] == bid_price_1
    assert auction_2_0['onAuction'] == True

    assert auction_2_1['auctionId'] == tx_bid_2_1.return_value
    assert auction_2_1['tokenAddress'] == emograms
    assert auction_2_1['tokenId'] == 2
    assert auction_2_1['seller'] == accounts[1]
    assert auction_2_1['highestBidder'] == accounts[3]
    assert auction_2_1['startPrice'] == sell_price
    assert auction_2_1['highestBid'] == bid_price_2
    assert auction_2_1['onAuction'] == True

    # Asserting BidPlaced events
    assert tx_bid_2_0.events['BidPlaced']['id'] == 0
    assert tx_bid_2_0.events['BidPlaced']['tokenId'] == 2
    assert tx_bid_2_0.events['BidPlaced']['bidder'] == accounts[2]
    assert tx_bid_2_0.events['BidPlaced']['bid'] == bid_price_1

    assert tx_bid_2_1.events['BidPlaced']['id'] == 0
    assert tx_bid_2_1.events['BidPlaced']['tokenId'] == 2
    assert tx_bid_2_1.events['BidPlaced']['bidder'] == accounts[3]
    assert tx_bid_2_1.events['BidPlaced']['bid'] == bid_price_2

    # Check if the auction can be finished before endDate
    try: 
        marketplace.finishAuction(emograms, 3, 1, {'from': accounts[0]})
    except Exception as e:
        assert 'Auction is still ongoing' in e.revert_msg
    
    # Wait for endDate and finish auctions
    time.sleep(auction_time+1)
    tx_finish_bid = marketplace.finishAuction(emograms, 2, 0, {'from': accounts[1]})
    tx_finish_nobid = marketplace.finishAuction(emograms, 3, 1, {'from': accounts[0]})
    
    # Token balance checks
    assert emograms.balanceOf(accounts[0], 2, {'from': accounts[0]}) == 0
    assert emograms.balanceOf(accounts[1], 2, {'from': accounts[0]}) == 0
    assert emograms.balanceOf(accounts[2], 2, {'from': accounts[0]}) == 0
    assert emograms.balanceOf(accounts[3], 2, {'from': accounts[0]}) == 1

    assert emograms.balanceOf(accounts[0], 3, {'from': accounts[0]}) == 1
    assert emograms.balanceOf(accounts[1], 3, {'from': accounts[0]}) == 0
    assert emograms.balanceOf(accounts[2], 3, {'from': accounts[0]}) == 0
    assert emograms.balanceOf(accounts[3], 3, {'from': accounts[0]}) == 0

    # ETH balance checks
    assert accounts[0].balance() == seller_init_balance_1 + bid_price_2*royalty_pct
    assert accounts[1].balance() == seller_init_balance_2 + bid_price_2 - bid_price_2*royalty_pct
    assert accounts[2].balance() == buyer_init_balance_1
    assert accounts[3].balance() == buyer_init_balance_2 - bid_price_2

    # Event checks
    assert tx_finish_bid.events['AuctionFinished']['id'] == 0
    assert tx_finish_bid.events['AuctionFinished']['tokenId'] == 2
    assert tx_finish_bid.events['AuctionFinished']['highestBidder'] == accounts[3]
    assert tx_finish_bid.events['AuctionFinished']['seller'] == accounts[1]
    assert tx_finish_bid.events['AuctionFinished']['highestBid'] == bid_price_2

    assert tx_finish_nobid.events['AuctionFinished']['id'] == 1
    assert tx_finish_nobid.events['AuctionFinished']['tokenId'] == 3
    assert tx_finish_nobid.events['AuctionFinished']['highestBidder'] == accounts[0]
    assert tx_finish_nobid.events['AuctionFinished']['seller'] == accounts[0]
    assert tx_finish_nobid.events['AuctionFinished']['highestBid'] == sell_price

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
    marketplace = EmogramMarketplaceUpgradeable.deploy({'from': accounts[0]})
    marketplace.initialize(True, {'from': accounts[0]})
    
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
            emogram_id = initial_order[i]
            print('Emogram id #%s' %(emogram_id))
            # Do checks
            tx = marketplace.emogramsOnAuction(i)
            print(tx)
            assert tx['onAuction'] == True
            assert tx['tokenId'] == emogram_id
            assert tx['startPrice'] == price
            if idx>0:
                tx = marketplace.emogramsOnAuction(i-3)
                assert tx['onAuction'] == False

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

    print('current cycle: ', str(marketplace.initialAuction()))
    # Close last cycle
    step_auction = marketplace.stepAuctions(emograms, price, auction_time)

    # Check if initialAuction period ended and all auctions are closed
    assert 'InitialAuctionFinished' in step_auction.events

    print('last check')
    for idx, i in enumerate(range(0,99)):
        tx = marketplace.emogramsOnAuction(i)
        print(idx, i, tx)
        assert tx['onAuction'] == False

def test_srt_distribution():
    '''
    Test SRT distribution after public auction
    '''
    auction_duration = 2

    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplaceUpgradeable.deploy({'from': accounts[0]})
    marketplace.initialize(True, {'from': accounts[0]})
        
    initial_order = [x for x in range(2,101)]
    assert len(initial_order) == 99
    marketplace.setInitialorder(initial_order)

    mint_token_ids = list(range(1, 101))
    mint_amounts = [1 for i in range(99)]
    mint_amounts.insert(0,110)  # Insert SRT amounts
    emograms.mintBatch(accounts[0], mint_token_ids, mint_amounts, "")
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[0]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[1]})

    # Iterate over auction period
    for x in range(0,33):
        step_auction = marketplace.stepAuctions(emograms, 0.1e18, auction_duration)
        for i in range(3*x,3*x+3):
            print('Auction cycle #%s' %(x))
            tx = marketplace.emogramsOnAuction(i)
            marketplace.PlaceBid(i, tx['tokenId'], emograms, {'from': accounts[1], 'value': 0.2e18})
    step_auction = marketplace.stepAuctions(emograms, 0.1e18, 1)

    # Distribute after auction period
    emograms.distributeSRT(accounts[0])

    # Check if distributed amounts are correct
    assert emograms.balanceOf(accounts[1], 1) == 99
    

def test_founder_vault_royalties():
    '''
    Deploying founder vault and setting as beneficiary in marketplace contract.
    Making a sell auction and fixed price transaction and checking royalties in founder vault
    '''
    # Setting addresses
    CSONGOR = accounts[9]
    PATR = accounts[8]
    ADR = accounts[7]
    MIKI = accounts[6]

    # Miki, Csongor, Patr, Adr
    founders = [MIKI, CSONGOR, PATR, ADR]
    founders_pct = [50, 5, 22.5, 22.5]
    founders_pct = [x*100 for x in founders_pct]

    # Deploying contracts
    vault = FounderVault.deploy(founders, founders_pct, {'from': accounts[0]})
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplaceUpgradeable.deploy({'from': accounts[0]})
    marketplace.initialize(True, {'from': accounts[0]})

    # Setting approvals
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[0]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[1]})

    # Setting beneficiaries
    emograms.setBeneficiary(vault)

    # Minting emograms
    token_id_auction = 2
    token_id_auction_nobid = 3
    token_id_fixed = 4
    token_id_fixed_nobuy = 5
    sell_price = 1e18
    bid_price = sell_price*1.1
    auction_time = 2
    royalty_pct = 0.075

    emograms.mintBatch(accounts[0], list(range(2, 101)), [1 for i in range(99)], "")

    # Selling on auction bid/nobid
    tx_auction_bid = marketplace.createAuction(token_id_auction, emograms, auction_time, sell_price, {'from': accounts[0]})
    tx_auction_nobid = marketplace.createAuction(token_id_auction_nobid, emograms, auction_time, sell_price, {'from': accounts[0]})
    auction_id = tx_auction_bid.return_value
    auction_id_nobid = tx_auction_nobid.return_value

    # Placing bid
    tx_bid = marketplace.PlaceBid(auction_id, token_id_auction, emograms, {'from': accounts[1], 'value': bid_price})
    auction_item = marketplace.emogramsOnAuction(auction_id)
    auction_item_nobid = marketplace.emogramsOnAuction(auction_id_nobid)

    # Finishing auctions
    time.sleep(auction_time+1)
    tx_finish_bid = marketplace.finishAuction(emograms, token_id_auction, auction_id, {'from': accounts[0]})
    tx_finish_nobid = marketplace.finishAuction(emograms, 3, 1, {'from': accounts[0]})

    # Selling on fixed price, buying and no buying
    tx_fixed = marketplace.addEmogramToMarket(token_id_fixed, emograms, sell_price, {'from': accounts[0]})
    tx_fixed_nobuy = marketplace.addEmogramToMarket(token_id_fixed_nobuy, emograms, sell_price, {'from': accounts[0]})
    sell_item = tx_fixed.return_value
    sell_item_nobuy = tx_fixed_nobuy.return_value
    tx_buy = marketplace.buyEmogram(sell_item, {'from': accounts[1], 'amount': sell_price})

    assert_vault_balance = sell_price * royalty_pct # Fixed buy
    assert_vault_balance += bid_price * royalty_pct # Auction 
    assert int(assert_vault_balance)/1 == vault.balance()/1

def test_vault_distribution():
    '''
    Test founder vault withdraw mechanism and assert balances
    '''

    # Amount to work with
    total_withdraw_amount = 1e18

    # Setting addresses
    CSONGOR = accounts[9]
    PATR = accounts[8]
    ADR = accounts[7]
    MIKI = accounts[6]
    
    CSONGOR_balance = accounts[9].balance()
    PATR_balance = accounts[8].balance()
    ADR_balance = accounts[7].balance()
    MIKI_balance = accounts[6].balance()

    # Miki, Csongor, Patr, Adr
    founders = [MIKI, CSONGOR, PATR, ADR]
    founders_pct = [50, 5, 22.5, 22.5]
    founders_pct = [x*100 for x in founders_pct]

    # Deploying contracts
    vault = FounderVault.deploy(founders, founders_pct, {'from': accounts[0]})
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplaceUpgradeable.deploy({'from': accounts[0]})
    marketplace.initialize(True, {'from': accounts[0]})
    vault_balance = vault.balance()

    # Get some funds to distribute
    accounts[0].transfer(vault, total_withdraw_amount)
    assert vault.balance() == vault_balance + total_withdraw_amount

    # Withdraw and assert
    vault.withdraw()
    # SafeMath.div(SafeMath.mul(totalContents, Percentages[Founders[i]]), 10000);
    assert MIKI.balance() == MIKI_balance + total_withdraw_amount*founders_pct[0]/10000
    assert CSONGOR.balance() == CSONGOR_balance + total_withdraw_amount*founders_pct[1]/10000
    assert PATR.balance() == PATR_balance + total_withdraw_amount*founders_pct[2]/10000
    assert ADR.balance() == ADR_balance + total_withdraw_amount*founders_pct[3]/10000
    assert vault.balance() == vault_balance + total_withdraw_amount - total_withdraw_amount

def test_proxy_deploy():
    '''
    Deploying contracts with proxy scheme and testing interactions
    '''
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplaceUpgradeable.deploy({'from': accounts[0]})
    marketplace_encoded_init_function = encode_function_data(True)
    proxy = ERC1967Proxy.deploy(marketplace, marketplace_encoded_init_function, {'from': accounts[0]})
    proxy_abi = Contract.from_abi("EmogramMarketplaceUpgradeable", proxy.address, EmogramMarketplaceUpgradeable.abi)
    proxy_abi.initialize(True, {'from': accounts[0]})
    emograms.createEmogram({'from': accounts[0]})
    emograms.setApprovalForAll(proxy_abi, True, {'from': accounts[0]})
    proxy_abi.addEmogramToMarket(2, emograms, 1e18, {'from': accounts[0]})
    sale = proxy_abi.emogramsOnSale(0)

    assert sale['sellId'] == 0
    assert sale['tokenAddress'] == emograms
    assert sale['tokenId'] == 2
    assert sale['seller'] == accounts[0]
    assert sale['price'] == 1e18
    assert sale['isSold'] == False
    
def test_proxy_upgrade():
    '''
    Deploying a proxy scheme and upgrading with a modified contract version
    '''
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
    sale_data = proxy_abi.emogramsOnSale(0)

    assert proxy_abi.emogramsOnSaleLength() == 1

    marketplace_v2 = EmogramMarketplaceUpgradeable_UpgradeTest.deploy({'from': accounts[0]})
    proxy_abi.upgradeTo(marketplace_v2, {'from': accounts[0]})
    proxy_abi_v2 = Contract.from_abi("EmogramMarketplaceUpgradeable_UpgradeTest", proxy.address, EmogramMarketplaceUpgradeable_UpgradeTest.abi)

    assert proxy_abi_v2.emogramsOnSaleLength() == 2
    newfunction = proxy_abi_v2.newFunction()
    assert newfunction == 'Upgraded'
    assert sale_data == proxy_abi_v2.emogramsOnSale(0)

def test_originality_test():
    hashes_str = []
    uuids_obj = []
    uuids_str = []

    for x in range(0,101):
        uuids_obj.append(uuid.uuid4())
        uuid_string = str(uuids_obj[x]).replace('-', '')
        uuids_str.append(uuid_string)
        hashes_str.append(hashlib.sha256(uuids_str[x].encode()).hexdigest())

    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplaceUpgradeable.deploy({'from': accounts[0]})
    marketplace.initialize(True, {'from': accounts[0]})

    emograms.setOrigHash(hashes_str)

    for x in range(0, 100):
        emograms.originalityHash(x)
        hashes_str[x]
        hashlib.sha256(uuids_str[x].encode()).hexdigest()
        returned_value = emograms.verifyOrig(bytes(uuids_str[x], 'UTF-8'), x+2).return_value
        assert returned_value == True

'''
Todo:
- test erc1155 trasnfer from foundervault after closed auction with no bid
'''

def test_no_bid_token_transfer_from_vault():
    '''
    Deploying founder vault and setting as beneficiary in marketplace contract.
    Making a sell auction and fixed price transaction and checking royalties in founder vault
    '''
    # Setting addresses
    CSONGOR = accounts[9]
    PATR = accounts[8]
    ADR = accounts[7]
    MIKI = accounts[6]

    # Miki, Csongor, Patr, Adr
    founders = [MIKI, CSONGOR, PATR, ADR]
    founders_pct = [50, 5, 22.5, 22.5]
    founders_pct = [x*100 for x in founders_pct]

    # Deploying contracts
    vault = FounderVault.deploy(founders, founders_pct, {'from': accounts[0]})
    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplaceUpgradeable.deploy({'from': accounts[0]})
    marketplace.initialize(True, {'from': accounts[0]})

    # Setting approvals
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[0]})
    emograms.setApprovalForAll(marketplace, True, {'from': accounts[1]})
    emograms.setApprovalForAll(marketplace, True, {'from': vault})

    # Setting beneficiaries
    emograms.setBeneficiary(vault)

    # Minting emograms
    token_id_auction = 2
    token_id_auction_nobid = 3
    token_id_fixed = 4
    token_id_fixed_nobuy = 5
    sell_price = 1e18
    bid_price = sell_price*1.1
    auction_time = 2
    royalty_pct = 0.075

    emograms.mintBatch(accounts[0], list(range(2, 101)), [1 for i in range(99)], "")
    emograms.safeTransferFrom(accounts[0], vault, token_id_auction_nobid, 1, '')

    # Selling on auction bid/nobid
    tx_auction_bid = marketplace.createAuction(token_id_auction, emograms, auction_time, sell_price, {'from': accounts[0]})
    tx_auction_nobid = marketplace.createAuction(token_id_auction_nobid, emograms, auction_time, sell_price, {'from': vault})
    auction_id = tx_auction_bid.return_value
    auction_id_nobid = tx_auction_nobid.return_value

    # Placing bid
    tx_bid = marketplace.PlaceBid(auction_id, token_id_auction, emograms, {'from': accounts[1], 'value': bid_price})
    try: 
        tx_bid = marketplace.PlaceBid(auction_id, token_id_auction, emograms, {'from': accounts[2], 'value': bid_price})
    except Exception as e:
        assert 'Bid too low' in e.revert_msg

    auction_item = marketplace.emogramsOnAuction(auction_id)
    auction_item_nobid = marketplace.emogramsOnAuction(auction_id_nobid)

    # Finishing auctions
    time.sleep(auction_time+1)
    tx_finish_bid = marketplace.finishAuction(emograms, token_id_auction, auction_id, {'from': accounts[0]})
    tx_finish_nobid = marketplace.finishAuction(emograms, token_id_auction_nobid, auction_id_nobid, {'from': vault})

    assert emograms.ownerOf(token_id_auction_nobid, vault) == True
    emograms.safeTransferFrom(vault, accounts[0], token_id_auction_nobid, 1, '', {'from': vault})
    assert emograms.ownerOf(token_id_auction_nobid, accounts[0]) == True

def test_full_workflow():
    """ Steps: 
                0. set addresses, constants
                1. deploy emogramsCollectible, marketplace, proxy, vault
                2. Mint emograms, SRT
                3: set initialOrder
                4. set origHash
                5. start stepauction from vault until finished
                6. bid randomly to auctions
                7. check balances, emogram owners, etc
                8. withdraw from wallet, trasnfer remaining emograms
    """

    # Setting addresses
    CSONGOR = accounts[9]
    PATR = accounts[8]
    ADR = accounts[7]
    MIKI = accounts[6]

    bid_price_1 = 1.1e18
    bid_price_2 = 1.2e18
    # Miki, Csongor, Patr, Adr
    founders = [MIKI, CSONGOR, PATR, ADR]
    founders_pct = [50, 5, 22.5, 22.5]
    founders_pct = [x*100 for x in founders_pct]

    emograms = EmogramsCollectible.deploy({'from': accounts[0]})
    marketplace = EmogramMarketplaceUpgradeable.deploy({'from': accounts[0]})
    marketplace_encoded_init_function = encode_function_data(True)
    proxy = ERC1967Proxy.deploy(marketplace, marketplace_encoded_init_function, {'from': accounts[0]})
    proxy_abi = Contract.from_abi("EmogramMarketplaceUpgradeable", proxy.address, EmogramMarketplaceUpgradeable.abi)
    proxy_abi.initialize(True, {'from': accounts[0]})
    vault = FounderVault.deploy(founders, founders_pct, {'from': accounts[0]})

    emograms.setApprovalForAll(proxy_abi, True, {'from': vault})
    emograms.setApprovalForAll(proxy_abi, True, {'from': accounts[0]})
    emograms.setApprovalForAll(proxy_abi, True, {'from': accounts[1]})

    # Setting beneficiaries
    emograms.setBeneficiary(vault)

    # Minting emograms
    token_id_auction = 2
    token_id_auction_nobid = 3
    token_id_fixed = 4
    token_id_fixed_nobuy = 5
    sell_price = 1e18
    bid_price = sell_price*1.1
    auction_time = 2
    royalty_pct = 0.075

    emograms.mintBatch(vault, list(range(2, 101)), [1 for i in range(99)], "")

    initial_auction_prices = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    for i in range(0, 33-len(initial_auction_prices)):
        initial_auction_prices.append(1.0)
    assert len(initial_auction_prices) == 33
    
    initial_order = [x for x in range(2,101)]
    random.shuffle(initial_order)
    assert len(initial_order) == 99
    proxy_abi.setInitialorder(initial_order, {'from': accounts[0]})
    proxy_abi.addFounder(vault, {'from': accounts[0]})
    accounts[0].transfer(vault, 1e18)
    assert vault.balance() != 0

    for idx, price in enumerate(initial_auction_prices):        
        print('Auction cycle #%s' %(idx))
        step_auction = proxy_abi.stepAuctions(emograms, price, auction_time, {'from': vault})
        for i in range(3*idx,3*idx+3):
            emogram_id = initial_order[i]
            print('Emogram id #%s' %(emogram_id))
            # Do checks
            tx = proxy_abi.emogramsOnAuction(i)
            print(tx)
            assert tx['onAuction'] == True
            assert tx['tokenId'] == emogram_id
            assert tx['startPrice'] == price
            if idx>0:
                tx = proxy_abi.emogramsOnAuction(i-3)
                assert tx['onAuction'] == False

        # Bid for only every 3
        if i%3==0:
            proxy_abi.PlaceBid(i, tx['tokenId'], emograms, {'from': accounts[2], 'value': bid_price_1})
            proxy_abi.PlaceBid(i, tx['tokenId'], emograms, {'from': accounts[3], 'value': bid_price_2})

        # Check if every third is owned by accounts[3] and the rest is owned by accounts[0]
        if idx > 0:
            if i%3==0:
                assert emograms.balanceOf(accounts[0], initial_order[idx], {'from': accounts[0]}) == 0
                assert emograms.balanceOf(accounts[2], initial_order[idx], {'from': accounts[0]}) == 0
                assert emograms.balanceOf(accounts[3], initial_order[idx], {'from': accounts[0]}) == 1
            else:
                assert emograms.balanceOf(vault, initial_order[idx], {'from': accounts[0]}) == 1
                assert emograms.balanceOf(accounts[2], initial_order[idx], {'from': accounts[0]}) == 0
                assert emograms.balanceOf(accounts[3], initial_order[idx], {'from': accounts[0]}) == 0

    print('current cycle: ', str(proxy_abi.initialAuction()))
    # Close last cycle
    step_auction = proxy_abi.stepAuctions(emograms, price, auction_time, {'from': vault})

    # Check if initialAuction period ended and all auctions are closed
    assert 'InitialAuctionFinished' in step_auction.events

    print('last check')
    for idx, i in enumerate(range(0,99)):
        tx = proxy_abi.emogramsOnAuction(i)
        print(idx, i, tx)
        assert tx['onAuction'] == False

    assert proxy.balance() == 0
    assert vault.balance() != 0
    print(vault.balance())
    print(proxy.balance())

