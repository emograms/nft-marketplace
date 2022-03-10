"""
TODO:
-set WETH/TST address in marketplace init
-mint SRT
"""







import eth_utils, random, json, requests, time, os
clear = lambda: os.system('clear')
import time
import brownie
from brownie import EmogramsCollectible, EmogramMarketplaceUpgradeable, FounderVault, ERC1967Proxy, ScultureRedemptionToken, accounts, network
from brownie.network.gas.strategies import GasNowStrategy
from brownie.network import gas_price, priority_fee
from brownie import Contract

# VARS
IPFS_URI = 'https://cloudflare-ipfs.com/ipfs/QmdLiV539qPnN9tcUikV5NPD5DWSED1uzGFFa3wvX9ent7/{id}/'
IPFS_JSON = requests.get(IPFS_URI.replace('{id}/', '0')).json()
ORIGIN_HASHES = [IPFS_JSON[str(x)]['description'] for x in range(2,101)]
ETHERSCAN_API = 'X7BGUXQ4E3TYHKX6KGIJW7EM6RVEWFVPUM'
os.environ["ETHERSCAN_TOKEN"] = ETHERSCAN_API

# WALLETS
DEPLOYER =  'c53152e574f8df7447caaa310622955bd9ae0f5a1b087fde9007ccbdb962f1a9'      #'0xb501ec584f99BD7fa536A8a83ebCf413282193eb'
accounts.add(DEPLOYER)
DEPLOYER = accounts[0]

# WETH (polygon mainnet), TST (mumbai) addresses
WETH = '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619'
TST = '0x2d7882beDcbfDDce29Ba99965dd3cdF7fcB10A1e'

print('\n----- Deployment script loaded -----')
print("Active Network: ")
print(network.show_active() + "\n")
if network.show_active() != 'mumbai':
    print("ATTENTION: YOPU ARE DEPLOYING TO POLYGON MAINNET")
print('Wallet addreses used:')
print('DEPLOYER:', DEPLOYER)
print('\nUse set_gas() before interacting!')


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
            return None, None, None, None

def loadJSONRaw():
    if os.path.isfile(DEPLOYMENT_JSON_PATH):
        with open(DEPLOYMENT_JSON_PATH) as json_file:
            deploymen_json = json.load(json_file)
        return deploymen_json

# Loading deploymend and IPFS JSONs
DEPLOYMENT_JSON_PATH = 'latest_deployment.json'
EMOGRAMMARKETPLACEUPGRADEABLE_JSON, EMOGRAMSCOLLECTIBLE_JSON, FOUNDERVAULT_JSON, PROXY_JSON = loadJSON()


def set_gas():
    '''
    Must be called to set required gas price from interactive mode
    '''
    global tx_params
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

# DEPLOYMENT
def deploy_network(testMode=False, publishSource=True, saveJSON=True):

    # Deploying contracts
    emograms = EmogramsCollectible.deploy(tx_params, publish_source=publishSource)
    SRToken = ScultureRedemptionToken.deploy(tx_params, publish_source=publishSource)
    marketplace_contract = EmogramMarketplaceUpgradeable.deploy(tx_params, publish_source=publishSource)
    marketplace_encoded_init_function = encode_function_data(True)
    proxy = ERC1967Proxy.deploy(marketplace_contract, marketplace_encoded_init_function, tx_params, publish_source=publishSource)
    marketplace_proxy = Contract.from_abi("EmogramMarketplaceUpgradeable", proxy.address, EmogramMarketplaceUpgradeable.abi)
    marketplace_proxy.initialize(testMode, tx_params)

    # Founder Vault deployment Miki, Csongor, Patr, Adr
    founders = [MIKI, CSONGOR, PATR, ADR]
    founders_pct = [0.5, 0.05, 0.225, 0.225]
    founders_pct = [x*10000 for x in founders_pct]
    vault = FounderVault.deploy(founders, founders_pct, tx_params, publish_source=publishSource)
    # Add founder role to vault
    marketplace_proxy.addFounder(vault, tx_params)

    print("Contracts deployed on:", network.show_active())

    # Set beneficiary on EmogramsCollectible
    emograms.setBeneficiary(vault)


