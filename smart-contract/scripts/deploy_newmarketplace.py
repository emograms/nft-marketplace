import eth_utils, random, json, requests, time, os
clear = lambda: os.system('clear')
import time
import brownie
from brownie import EmogramMarketplaceUpgradeable, accounts, network
from brownie.network.gas.strategies import GasNowStrategy
from brownie.network import gas_price, priority_fee
from brownie import Contract

# WALLETS
DEPLOYER =  'c53152e574f8df7447caaa310622955bd9ae0f5a1b087fde9007ccbdb962f1a9'      #'0xb501ec584f99BD7fa536A8a83ebCf413282193eb'
accounts.add(DEPLOYER)
DEPLOYER = accounts[0]

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


#DEPLOY
marketplace_contract = EmogramMarketplaceUpgradeable.deploy(tx_params, publish_source=publishSource)