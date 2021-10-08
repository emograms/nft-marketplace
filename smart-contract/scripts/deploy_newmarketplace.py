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

#DEPLOY
gas_input = int(brownie.web3.fromWei(GasNowStrategy("standard").get_gas_price(), "gwei"))
tx_params = {'from': DEPLOYER, 'priority_fee': gas_input}
marketplace_contract = EmogramMarketplaceUpgradeable.deploy(tx_params, publish_source=True)