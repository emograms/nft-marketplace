import os
import time
from brownie import EmogramsCollectible, accounts, network
from brownie.network.gas.strategies import GasNowStrategy

PRIVATE_KEY_GOERLI_PATR = '4a773f2fc786f73b56d6bc158eb1f82fde7c687b539c5e311696d670f6118a1a' #'0x6e1614190c37317a957368FDbC365262FC0A1E43'

# Init deployer address
accounts.add(PRIVATE_KEY_GOERLI_PATR)

PATR = accounts[0]

gas_strategy = GasNowStrategy("fast")

print('\n----- Test script loaded -----')
print("Active Network: ")
print(network.show_active() + "\n")
print("Fast Gas Price: ")
print(str(gas_strategy.get_gas_price()) + " wei \n")

emograms = EmogramsCollectible.deploy({'from': PATR})

emograms.createFunToken(1, 1, {'from': PATR})

for i in range(0, 3):
    emograms.createEmogram({'from': PATR})

emograms.setURI("https://cloudflare-ipfs.com/ipfs/QmXxU89wFqCBdWrcyjQ4ZbvC6KNZkGpwXvsn9VCUjaoEPK/{id}/", {'from': PATR, 'gas_price': gas_strategy})
print("URI6 SET")