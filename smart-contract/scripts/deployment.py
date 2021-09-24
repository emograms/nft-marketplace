import os
import time
import brownie
from brownie import EmogramsCollectible, EmogramMarketplaceUpgradeable, FounderVault, ERC1967Proxy, accounts, network
from brownie.network.gas.strategies import GasNowStrategy
from brownie.network import gas_price, priority_fee
from brownie import Contract
import eth_utils
import random
import json

# VARS
IPFS_URI = 'https://cloudflare-ipfs.com/ipfs/QmPAPuuiuoqX4gQTbk1jMDHgRe8LML5Bd1beUrM3RDswVq/{id}/'
ETHERSCAN_API = 'X7BGUXQ4E3TYHKX6KGIJW7EM6RVEWFVPUM'

# WALLETS
PRIVATE_KEY_GOERLI_MIKI = '3a8bb854c7a86d950c0d3e0b5b1bbcd3912389a95fa530e46c911fe1de099808'        #'0xFe594E862c3ce76E192997EABFC41Afd7C975b52'
PRIVATE_KEY_GOERLI_CSONGOR = '7890e57df5d235ca4a5065341467d18276293f7066bf96e7e9a88c6f89737c67'     #'0x76cA42252508c0AD52bf7936dC3eabb82cF9872e'
PRIVATE_KEY_GOERLI_PATR = 'fd290876475f82321cb0c142893c150fda939e9a3a3360715456f734eaef8831'        #'0xE7E8FB1932084E3BbE382EbaCdc16D835B30216F'
PRIVATE_KEY_GOERLI_ADR = '5ffe2515807d0ace67c342183c6aa506f25553d7fa0e93ceeb4d9b77b55128a2'         #'0xA558c9148846F17AcD9E99D8a8D0D1ECdCf0c7fA'
PRIVATE_KEY_GOERLI_DEPLOYER = 'c53152e574f8df7447caaa310622955bd9ae0f5a1b087fde9007ccbdb962f1a9'    #'0xb501ec584f99BD7fa536A8a83ebCf413282193eb'

# Deployed contracts if there are such
EMOGRAMMARKETPLACEUPGRADEABLE = '0x300c6828eEFAefb3C31269eD0463D86E6B4B0eC5'
EMOGRAMSCOLLECTIBLE = '0x39FF6aA0791cD8E85C64594e08f4deC9Bbd7783A'
FOUNDERVAULT = '0x712446f24c4511F391b590Eb885BB9dAC5C58944'
PROXY = ''

# Loading DEPLOYMENT_JSON_PATH for contract loading 
def loadJSON():
    if os.path.isfile(DEPLOYMENT_JSON_PATH):
        with open(DEPLOYMENT_JSON_PATH) as json_file:
            deploymen_json = json.load(json_file)
        if network.show_active() in deploymen_json.keys():
            EMOGRAMMARKETPLACEUPGRADEABLE_JSON = deploymen_json[network.show_active()]['EMOGRAMMARKETPLACEUPGRADEABLE']
            EMOGRAMSCOLLECTIBLE_JSON = deploymen_json[network.show_active()]['EMOGRAMSCOLLECTIBLE']
            FOUNDERVAULT_JSON = deploymen_json[network.show_active()]['FOUNDERVAULT']
            PROXY_JSON = deploymen_json[network.show_active()]['PROXY']
            return EMOGRAMMARKETPLACEUPGRADEABLE_JSON, EMOGRAMSCOLLECTIBLE_JSON, FOUNDERVAULT_JSON, PROXY_JSON
        else:
            return '0x0', '0x0', '0x0', '0x0'
    else:
        return '0x0', '0x0', '0x0', '0x0'

def loadJSONRaw():
    if os.path.isfile(DEPLOYMENT_JSON_PATH):
        with open(DEPLOYMENT_JSON_PATH) as json_file:
            deploymen_json = json.load(json_file)
        return deploymen_json

# Loading
DEPLOYMENT_JSON_PATH = 'latest_deployment.json'
EMOGRAMMARKETPLACEUPGRADEABLE_JSON, EMOGRAMSCOLLECTIBLE_JSON, FOUNDERVAULT_JSON, PROXY_JSON = loadJSON()

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

# Setting gas prices for interactions
if network.show_active() == 'development':
    gas_input = input("Please define a gas fee you would like to use (gwei):")
    gas_input = brownie.web3.toWei(int(gas_input), "gwei")
    gas_price(gas_input)
    tx_params = {'from': DEPLOYER, 'gas_price': gas_input}

# mainnet, goerli, kovan, ropsten, etc. anything
else:
    if network.show_active() == 'mainnet':
        print("Which gas price strategy would you like to use?")
        fee_type_input = input("GasNow or EIP1559: ")

        if fee_type_input == 'EIP1559':
            eip1559_fee_input = input("Set a priority fee (gwei):")
            gas_input = priority_fee(brownie.web3.toWei(int(eip1559_fee_input), "gwei"))
            tx_params = {'from': DEPLOYER, 'priority_fee': gas_input}

        elif fee_type_input == 'GasNow':
            slow = int(brownie.web3.fromWei(GasNowStrategy("slow").get_gas_price(), "gwei"))
            standard = int(brownie.web3.fromWei(GasNowStrategy("standard").get_gas_price(), "gwei"))
            fast = int(brownie.web3.fromWei(GasNowStrategy("fast").get_gas_price(), "gwei"))
            rapid = int(brownie.web3.fromWei(GasNowStrategy("rapid").get_gas_price(), "gwei"))
            print("Mainnet Gas Prices: \n")
            print("Slow: ", str(slow) + " gwei")
            print("Standard: ", str(standard) + " gwei")
            print("Fast: ", str(fast) + " gwei")
            print("Rapid: ", str(rapid) + " gwei \n")
            gas_input = input("Which gas speed would you like to use? (slow/standard/fast/rapid): ")
            gas_input = GasNowStrategy(gas_input)
            gas_price(gas_input)
            gas_input = gas_input.get_gas_price()
            tx_params = {'from': DEPLOYER, 'gas_price': gas_input}


    else: # any testnet
        eip1559_fee_input = input("Please set an EIP1559 priority fee (gwei):")
        gas_input = priority_fee(brownie.web3.toWei(int(eip1559_fee_input), "gwei"))
        tx_params = {'from': DEPLOYER, 'priority_fee': gas_input}

# Displaying new prices
gas_price_gwei = brownie.web3.fromWei(gas_input, "gwei")
print('Gas prices set at: ', str(gas_price_gwei), ' gwei')



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
    
def load_deployed_contracts(withProxy=True, fromJSON=True):
    if fromJSON:
        EMOGRAMMARKETPLACEUPGRADEABLE_JSON, EMOGRAMSCOLLECTIBLE_JSON, FOUNDERVAULT_JSON, PROXY_JSON = loadJSON()
        emograms = Contract(EMOGRAMSCOLLECTIBLE_JSON)
        marketplace = Contract(EMOGRAMMARKETPLACEUPGRADEABLE_JSON)
        vault = Contract(FOUNDERVAULT_JSON)

        if withProxy:
            marketplace = Contract(PROXY_JSON)
    else:
        emograms = Contract(EMOGRAMSCOLLECTIBLE)
        marketplace = Contract(EMOGRAMMARKETPLACEUPGRADEABLE)
        vault = Contract(FOUNDERVAULT)

        if withProxy:
            marketplace = Contract(PROXY)
        
    return emograms, marketplace, vault
    
def deploy_network(withProxy=True, testMode=False, publishSource=True, saveJSON=True):

    # Deploying contracts
    emograms = EmogramsCollectible.deploy(tx_params, publish_source=publishSource)
    
    if withProxy:
        marketplace_contract = EmogramMarketplaceUpgradeable.deploy(tx_params, publish_source=publishSource)
        marketplace_encoded_init_function = encode_function_data(True)
        proxy = ERC1967Proxy.deploy(marketplace_contract, marketplace_encoded_init_function, tx_params, publish_source=publishSource)
        marketplace = Contract.from_abi("EmogramMarketplaceUpgradeable", proxy.address, EmogramMarketplaceUpgradeable.abi)
        marketplace.initialize(testMode, tx_params)
    else:
        marketplace = EmogramMarketplaceUpgradeable.deploy(tx_params, publish_source=publishSource)
        marketplace.initialize(testMode, tx_params)

    # Miki, Csongor, Patr, Adr
    founders = [MIKI, CSONGOR, PATR, ADR]
    founders_pct = [50, 5, 22.5, 22.5]
    founders_pct = [x*10000 for x in founders_pct]
    vault = FounderVault.deploy(founders, founders_pct, tx_params, publish_source=publishSource)

    print("Contracts deployed on:", network.show_active())

    # Set beneficiary on EmogramsCollectible
    emograms.setBeneficiary(vault)
    # Set initial auction order
    initial_auction_order = [x for x in range(2,101)]
    random.shuffle(initial_auction_order)
    assert len(initial_auction_order) == 99
    marketplace.setInitialorder(initial_auction_order, tx_params)
    # Set marketplace URI
    emograms.setURI(IPFS_URI, tx_params)

    # Set Approve for DEPLOYER
    emograms.setApprovalForAll(marketplace, True, tx_params)

    # Creating JSON with deployment addresses
    if saveJSON:
        try: 
            deployed_contracts_json = loadJSONRaw()
        except:
            deployed_contracts_json = {}
        if network.show_active() not in deployed_contracts_json: deployed_contracts_json[network.show_active()] = {} 
        deployed_contracts_json[network.show_active()]['EMOGRAMMARKETPLACEUPGRADEABLE'] = marketplace.address
        deployed_contracts_json[network.show_active()]['EMOGRAMSCOLLECTIBLE'] = emograms.address
        deployed_contracts_json[network.show_active()]['FOUNDERVAULT'] = vault.address
        try: 
            deployed_contracts_json[network.show_active()]['PROXY'] = proxy.address
        except:
            deployed_contracts_json[network.show_active()]['PROXY'] = '0x0'

        with open(DEPLOYMENT_JSON_PATH, 'w') as outfile:
            json.dump(deployed_contracts_json, outfile, indent=4, sort_keys=True)

    return emograms, marketplace, vault

def mint_tokens(emograms, marketplace):
    # Minting Emogram NFT tokens and SRTs
    mint_token_ids = list(range(1, 101))
    mint_amounts = [1 for i in range(99)]
    mint_amounts.insert(0,110)  # Insert SRT amounts
    emograms.mintBatch(DEPLOYER, mint_token_ids, mint_amounts, "", tx_params)

    # Checking total of Emogram tokens number
    y = 0
    for x in range(1, 101):
        if(emograms.balanceOf(DEPLOYER, x, {'from': DEPLOYER}) != 0):
            y = y + emograms.balanceOf(DEPLOYER, x, {'from': DEPLOYER})
    print("Total emograms minted: ", y)

# def approve_addresses(emograms, marketplace):
    # Approve addreses
    
    # emograms.setApprovalForAll(marketplace, True, {'from': MIKI, 'gas_price': gas_input})
    # emograms.setApprovalForAll(marketplace, True, {'from': CSONGOR, 'gas_price': gas_input})
    # emograms.setApprovalForAll(marketplace, True, {'from': PATR, 'gas_price': gas_input})
    # emograms.setApprovalForAll(marketplace, True, {'from': ADR, 'gas_price': gas_input})
    # emograms.setApprovalForAll(marketplace, True, tx_params)

def distribute_few_tokens(emograms):

    print('Distributing tokens to MIKI, CSONGOR, PATR, ADR...')
    # Emogram Tokens and SRTs
    emograms.safeBatchTransferFrom(DEPLOYER, MIKI, [1,2,3], [1,1,1],'', tx_params)
    emograms.safeBatchTransferFrom(DEPLOYER, CSONGOR, [1,4,5], [1,1,1],'', tx_params)
    emograms.safeBatchTransferFrom(DEPLOYER, PATR, [1,6,7], [1,1,1],'', tx_params)
    emograms.safeBatchTransferFrom(DEPLOYER, ADR, [1,8,9], [1,1,1],'', tx_params)

def distribute_ether(to, amount=2e18):

    DEPLOYER.transfer(to, amount, tx_params)

def run_initialAuction_cycles(emograms, marketplace, duration=INITIAL_AUCTION_DURATION):

    # Auction variables
    initial_auction_prices = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]
    for i in range(0, 33-len(initial_auction_prices)):
        initial_auction_prices.append(0.1)
    assert len(initial_auction_prices) == 33
    initial_auction_prices_e18 = []
    for i in initial_auction_prices:
        initial_auction_prices_e18.append(i*1e18)


    # Get current cycle and remove cycle times element from INITIAL_AUCTION_PRICES
    auction_cycle = marketplace.initialAuction()['cycle']
    for i in range(auction_cycle):
        initial_auction_prices_e18.pop(0)

    # Start iterating over initial auction cycles
    print('Auction cycle #%s' %(auction_cycle+1), ' Start price: ', initial_auction_prices_e18[0])
    marketplace.stepAuctions(emograms, initial_auction_prices_e18[0], duration, tx_params)