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
emograms2 = EmogramsCollectible.deploy({'from': PATR})
emograms3 = EmogramsCollectible.deploy({'from': PATR})
emograms4 = EmogramsCollectible.deploy({'from': PATR})
emograms5 = EmogramsCollectible.deploy({'from': PATR})
emograms6 = EmogramsCollectible.deploy({'from': PATR})

emograms.createFunToken(1, 1, {'from': PATR})

for i in range(0, 3):
    emograms.createEmogram({'from': PATR})

emograms2.createFunToken(1, 1, {'from': PATR})

for i in range(0, 3):
    emograms2.createEmogram({'from': PATR})

emograms3.createFunToken(1, 1, {'from': PATR})

for i in range(0, 3):
    emograms3.createEmogram({'from': PATR})

emograms4.createFunToken(1, 1, {'from': PATR})

for i in range(0, 3):
    emograms4.createEmogram({'from': PATR})

emograms5.createFunToken(1, 1, {'from': PATR})

for i in range(0, 3):
    emograms5.createEmogram({'from': PATR})

emograms6.createFunToken(1, 1, {'from': PATR})

for i in range(0, 3):
    emograms6.createEmogram({'from': PATR})

emograms.setURI("ipfs://QmQsnoBbhrvxDJuwFG32CjEWNDQJTgEtgQ24BcUTTTFhzX/", {'from': PATR, 'gas_price': gas_strategy})
print("URI1 SET")
emograms2.setURI("https://cloudflare-ipfs.com/ipfs/QmQsnoBbhrvxDJuwFG32CjEWNDQJTgEtgQ24BcUTTTFhzX/", {'from': PATR, 'gas_price': gas_strategy})
print("URI2 SET")
emograms3.setURI("https://cloudflare-ipfs.com/ipfs/QmQsnoBbhrvxDJuwFG32CjEWNDQJTgEtgQ24BcUTTTFhzX/{id}/", {'from': PATR, 'gas_price': gas_strategy})
print("URI3 SET")
emograms4.setURI("ipfs://QmPAPuuiuoqX4gQTbk1jMDHgRe8LML5Bd1beUrM3RDswVq/", {'from': PATR, 'gas_price': gas_strategy})
print("URI4 SET")
emograms5.setURI("https://cloudflare-ipfs.com/ipfs/QmPAPuuiuoqX4gQTbk1jMDHgRe8LML5Bd1beUrM3RDswVq/", {'from': PATR, 'gas_price': gas_strategy})
print("URI5 SET")
emograms6.setURI("https://cloudflare-ipfs.com/ipfs/QmPAPuuiuoqX4gQTbk1jMDHgRe8LML5Bd1beUrM3RDswVq/{id}/", {'from': PATR, 'gas_price': gas_strategy})
print("URI6 SET")