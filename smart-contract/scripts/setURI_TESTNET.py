import os
import time
from brownie import EmogramsCollectible, EmogramMarketplace, EmogramsMarketplaceProxy, FounderVault, accounts, network
from brownie.network.gas.strategies import GasNowStrategy

PRIVATE_KEY_GOERLI_PATR = 'fd290876475f82321cb0c142893c150fda939e9a3a3360715456f734eaef8831' #'0xE7E8FB1932084E3BbE382EbaCdc16D835B30216F'
PRIVATE_KEY_GOERLI_DEPLOYER = 'c53152e574f8df7447caaa310622955bd9ae0f5a1b087fde9007ccbdb962f1a9'

# Init deployer address
accounts.add(PRIVATE_KEY_GOERLI_PATR)
accounts.add(PRIVATE_KEY_GOERLI_DEPLOYER)

PATR = accounts[0]
DEPLOYER = accounts[1]

gas_strategy = GasNowStrategy("fast")
os.environ["ETHERSCAN_TOKEN"] = ETHERSCAN_API

print('\n----- Deployment script loaded -----')
print("Active Network: ")
print(network.show_active() + "\n")
print("Fast Gas Price: ")
print(str(gas_strategy.get_gas_price()) + " wei \n")  
    
emograms.setURI("ipfs://QmRdjXwcVcxzZvoKjHy1uK6WegwGyi4WZDmsXP9p5VCrYh/", {'from': DEPLOYER, 'gas_price': gas_strategy})
print("URI SET")