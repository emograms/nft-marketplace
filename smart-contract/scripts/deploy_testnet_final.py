import os
import time
from brownie import EmogramsCollectible, EmogramMarketplaceUpgradeable, FounderVault, ERC1967Proxy, accounts, network
from brownie.network.gas.strategies import GasNowStrategy
from brownie import Contract
import eth_utils
import random

# VARS
IPFS_URI = 'https://cloudflare-ipfs.com/ipfs/QmQsnoBbhrvxDJuwFG32CjEWNDQJTgEtgQ24BcUTTTFhzX'
ETHERSCAN_API = 'X7BGUXQ4E3TYHKX6KGIJW7EM6RVEWFVPUM'

# WALLETS
PRIVATE_KEY_GOERLI_MIKI = '3a8bb854c7a86d950c0d3e0b5b1bbcd3912389a95fa530e46c911fe1de099808'        #'0xFe594E862c3ce76E192997EABFC41Afd7C975b52'
PRIVATE_KEY_GOERLI_CSONGOR = '7890e57df5d235ca4a5065341467d18276293f7066bf96e7e9a88c6f89737c67'     #'0x76cA42252508c0AD52bf7936dC3eabb82cF9872e'
PRIVATE_KEY_GOERLI_PATR = 'fd290876475f82321cb0c142893c150fda939e9a3a3360715456f734eaef8831'        #'0xE7E8FB1932084E3BbE382EbaCdc16D835B30216F'
PRIVATE_KEY_GOERLI_ADR = '5ffe2515807d0ace67c342183c6aa506f25553d7fa0e93ceeb4d9b77b55128a2'         #'0xA558c9148846F17AcD9E99D8a8D0D1ECdCf0c7fA'
PRIVATE_KEY_GOERLI_DEPLOYER = 'c53152e574f8df7447caaa310622955bd9ae0f5a1b087fde9007ccbdb962f1a9'    #'0xb501ec584f99BD7fa536A8a83ebCf413282193eb'

EMOGRAMMARKETPLACEUPGRADEABLE = '0x8775765ff680a9118c1f3ff17DaB2C9020D5Ce09'
EMOGRAMSCOLLECTIBLE = '0x4Db300e3Afc6D1b7AFFD6aEc51E285f3B647De4a'
FOUNDERVAULT = '0x5aB7Ae59190FFb3D6A93bD0858BB9D3714b038Cf'
PROXY = ''


# Init deployer address
accounts.add(PRIVATE_KEY_GOERLI_MIKI)
accounts.add(PRIVATE_KEY_GOERLI_CSONGOR)
accounts.add(PRIVATE_KEY_GOERLI_PATR)
accounts.add(PRIVATE_KEY_GOERLI_ADR)
accounts.add(PRIVATE_KEY_GOERLI_DEPLOYER)

MIKI = accounts[0]
CSONGOR = accounts[1]
PATR = accounts[2]
ADR = accounts[3]
DEPLOYER = accounts[4]

os.environ["ETHERSCAN_TOKEN"] = ETHERSCAN_API

# Setting intial auction duration and initial order
INITIAL_AUCTION_DURATION = 90

print('\n----- Deployment script loaded -----')
print("Active Network: ")
print(network.show_active() + "\n")
print("Fast Gas Price: ")
print(str(GasNowStrategy("fast").get_gas_price()) + " wei \n")


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
    
def load_deployed_contracts(withProxy=True):

    emograms = Contract(EMOGRAMSCOLLECTIBLE)
    marketplace = Contract(EMOGRAMMARKETPLACEUPGRADEABLE)
    vault = Contract(FOUNDERVAULT)

    if withProxy:
        marketplace = Contract(PROXY)
    
    return emograms, marketplace, vault
    

def deploy_network(withProxy=True, testMode=False, publishSource=True):

    # Deploying contracts
    emograms = EmogramsCollectible.deploy({'from': DEPLOYER, 'gas_price': GasNowStrategy("fast")}, publish_source=publishSource)
    
    if withProxy:
        marketplace_contract = EmogramMarketplaceUpgradeable.deploy({'from': DEPLOYER, 'gas_price': GasNowStrategy("fast")}, publish_source=publishSource)
        marketplace_encoded_init_function = encode_function_data(True)
        proxy = ERC1967Proxy.deploy(marketplace_contract, marketplace_encoded_init_function, {'from': DEPLOYER, 'gas_price': GasNowStrategy("fast")}, publish_source=publishSource)
        marketplace = Contract.from_abi("EmogramMarketplaceUpgradeable", proxy.address, EmogramMarketplaceUpgradeable.abi)
        marketplace.initialize(testMode, {'from': DEPLOYER, 'gas_price': GasNowStrategy("fast")})
    else:
        marketplace = EmogramMarketplaceUpgradeable.deploy({'from': DEPLOYER, 'gas_price': GasNowStrategy("fast")}, publish_source=publishSource)
        marketplace.initialize(testMode, {'from': DEPLOYER, 'gas_price': GasNowStrategy("fast")})

    # Miki, Csongor, Patr, Adr
    founders = [MIKI, CSONGOR, PATR, ADR]
    founders_pct = [50, 5, 22.5, 22.5]
    founders_pct = [x*10000 for x in founders_pct]
    vault = FounderVault.deploy(founders, founders_pct, {'from': DEPLOYER, 'gas_price': GasNowStrategy("fast")}, publish_source=publishSource)

    print("Contracts deployed on:", network.show_active())

    # Set beneficiary on EmogramsCollectible
    emograms.setBeneficiary(vault)
    # Set initial auction order
    initial_auction_order = [x for x in range(2,101)]
    random.shuffle(initial_auction_order)
    assert len(initial_auction_order) == 99
    marketplace.setInitialorder(initial_auction_order, {'from': DEPLOYER, 'gas_price': GasNowStrategy("fast")})
    # Set marketplace URI
    emograms.setURI(IPFS_URI, {'from': DEPLOYER, 'gas_price': GasNowStrategy("fast")})

    return emograms, marketplace, vault

def mint_tokens(emograms, marketplace):
    # Minting Emogram NFT tokens and SRTs
    mint_token_ids = list(range(1, 101))
    mint_amounts = [1 for i in range(99)]
    mint_amounts.insert(0,110)  # Insert SRT amounts
    emograms.mintBatch(DEPLOYER, mint_token_ids, mint_amounts, "", {'from': DEPLOYER, 'gas_price': GasNowStrategy("fast")})

    # Checking total of Emogram tokens number
    y = 0
    for x in range(1, 101):
        if(emograms.balanceOf(DEPLOYER, x, {'from': DEPLOYER}) != 0):
            y = y + emograms.balanceOf(DEPLOYER, x, {'from': DEPLOYER})
    print("Total emograms minted: ", y)


y = 0
for x in range(1, 101):
    if(emograms.balanceOf(d.DEPLOYER, x, {'from': d.DEPLOYER}) != 0):
        y = y + emograms.balanceOf(d.DEPLOYER, x, {'from': d.DEPLOYER})

    # Approve addreses
    emograms.setApprovalForAll(marketplace, True, {'from': MIKI, 'gas_price': GasNowStrategy("fast")})
    emograms.setApprovalForAll(marketplace, True, {'from': CSONGOR, 'gas_price': GasNowStrategy("fast")})
    emograms.setApprovalForAll(marketplace, True, {'from': PATR, 'gas_price': GasNowStrategy("fast")})
    emograms.setApprovalForAll(marketplace, True, {'from': ADR, 'gas_price': GasNowStrategy("fast")})
    emograms.setApprovalForAll(marketplace, True, {'from': DEPLOYER, 'gas_price': GasNowStrategy("fast")})


def distribute_few_tokens(emograms):

    print('Distributing tokens to MIKI, CSONGOR, PATR, ADR...')
    # Emogram Tokens and SRTs
    emograms.safeBatchTransferFrom(DEPLOYER, MIKI, [1,2,3], [1,1,1],'', {'from': DEPLOYER, 'gas_price': GasNowStrategy("fast")})
    emograms.safeBatchTransferFrom(DEPLOYER, CSONGOR, [1,4,5], [1,1,1],'', {'from': DEPLOYER, 'gas_price': GasNowStrategy("fast")})
    emograms.safeBatchTransferFrom(DEPLOYER, PATR, [1,6,7], [1,1,1],'', {'from': DEPLOYER, 'gas_price': GasNowStrategy("fast")})
    emograms.safeBatchTransferFrom(DEPLOYER, ADR, [1,8,9], [1,1,1],'', {'from': DEPLOYER, 'gas_price': GasNowStrategy("fast")})

def distribute_ether(to, amount=2e18):

    DEPLOYER.transfer(to, amount, {'gas_price': GasNowStrategy("fast")})

def run_initialAuction_cycles(emograms, marketplace, duration=INITIAL_AUCTION_DURATION):

    # Auction variables
    initial_auction_prices = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]
    for i in range(0, 33-len(initial_auction_prices)):
        initial_auction_prices.append(0.1)
    assert len(initial_auction_prices) == 33

    # Get current cycle and remove cycle times element from INITIAL_AUCTION_PRICES
    auction_cycle = marketplace.initialAuction()['cycle']
    for i in range(auction_cycle):
        initial_auction_prices.pop(0)

    # Start iterating over initial auction cycles
    print('Auction cycle #%s' %(auction_cycle+1))
    marketplace.stepAuctions(emograms, initial_auction_prices[0], duration, {'from': DEPLOYER, 'gas_price': GasNowStrategy("fast")})
