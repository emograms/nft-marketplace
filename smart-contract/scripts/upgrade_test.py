import os
import time
import eth_utils
import random
import brownie
from brownie import EmogramsCollectible, EmogramMarketplaceUpgradeable, FounderVault, ERC1967Proxy, EmogramMarketplaceUpgradeable_UpgradeTest, accounts, network
from brownie.network.gas.strategies import GasNowStrategy
from brownie.network import gas_price, priority_fee
from brownie import Contract


PRIVATE_KEY_GOERLI_PATR = 'fd290876475f82321cb0c142893c150fda939e9a3a3360715456f734eaef8831' #'0xE7E8FB1932084E3BbE382EbaCdc16D835B30216F'
PRIVATE_KEY_GOERLI_DEPLOYER = 'c53152e574f8df7447caaa310622955bd9ae0f5a1b087fde9007ccbdb962f1a9'

# Init deployer address
accounts.add(PRIVATE_KEY_GOERLI_PATR)
accounts.add(PRIVATE_KEY_GOERLI_DEPLOYER)

PATR = accounts[0]
DEPLOYER = accounts[1]

gas_strategy = GasNowStrategy("fast")
ETHERSCAN_API = 'X7BGUXQ4E3TYHKX6KGIJW7EM6RVEWFVPUM'
os.environ["ETHERSCAN_TOKEN"] = ETHERSCAN_API

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

print('\n----- Deployment script loaded -----')
print("Active Network: ")
print(network.show_active() + "\n")
print("Fast Gas Price: ")
print(str(gas_strategy.get_gas_price()) + " wei \n")


emograms = EmogramsCollectible.deploy({'from': accounts[0]}, publish_source=True)
marketplace = EmogramMarketplaceUpgradeable_UpgradeTest.deploy({'from': accounts[0]}, publish_source=True)
marketplace_encoded_init_function = encode_function_data(True)
proxy = ERC1967Proxy.deploy(marketplace, marketplace_encoded_init_function, {'from': accounts[0]}, publish_source=True)
proxy_abi = Contract.from_abi("EmogramMarketplaceUpgradeable_UpgradeTest", proxy.address, EmogramMarketplaceUpgradeable_UpgradeTest.abi)
proxy_abi.initialize(True, {'from': accounts[0]})

emograms.setApprovalForAll(proxy_abi, True, {'from': accounts[0]})
initial_order = [x for x in range(2,101)]
random.shuffle(initial_order)
assert len(initial_order) == 99

emograms.mintBatch(accounts[0], list(range(2, 101)), [1 for i in range(99)], "", {'from': accounts[0]})

proxy_abi.setInitialorder(initial_order, {'from': accounts[0]})

proxy_abi.stepAuctions(emograms, 0.1, 2, {'from': accounts[0]})

time.sleep(2)
proxy_abi.stepAuctions(emograms, 0.1, 2, {'from': accounts[0]})
time.sleep(2)

marketplace_v2 = EmogramMarketplaceUpgradeable.deploy({'from': accounts[0]}, publish_source=True)
#proxy_abi.upgradeTo(marketplace_v2, {'from': accounts[0]})
""" proxy_abi_v2 = Contract.from_abi("EmogramMarketplaceUpgradeable", proxy.address, EmogramMarketplaceUpgradeable.abi)


proxy_abi_v2.stepAuctions(emograms, 0.1, 2, {'from': accounts[0]})
time.sleep(2)

for x in range(0,9):
    print(proxy_abi_v2.emogramsOnAuction(x))

proxy_abi_v2.stepAuctions(emograms, 0.1, 2, {'from': accounts[0]})
time.sleep(2)

for x in range(0,12):
    print(proxy_abi_v2.emogramsOnAuction(x)) """