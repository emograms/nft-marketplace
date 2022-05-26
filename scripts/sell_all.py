import scripts.polygon_mainnet_deploy as d
import json

with open('latest_deployment.json', 'r') as deployments:
    addresses = json.load(deployments)
    marketplace_proxy_address = addresses['polygon-main']['PROXY']
    emograms_address = addresses['polygon-main']['EMOGRAMSCOLLECTIBLE']
    DEPLOYER = '3365973dff537bf0899c163c867787afdbb5d368bea82d03d1d0fb299e53d15a'
    d.accounts.add(DEPLOYER)
    #  As there is already an account added in the script imported above, so I take the last element added
    DEPLOYER = d.accounts[-1]
    print('Loaded marketplace proxy at:', marketplace_proxy_address)
    print('Loaded emograms at:', emograms_address)
    print('Loaded deployer at:', DEPLOYER.address)


def main():
    d.set_gas(DEPLOYER)
    start = input("Ready to start (y/n)")
    if start == 'y':
        marketplace = d.EmogramMarketplaceUpgradeable.at(
            marketplace_proxy_address)
        emograms = d.EmogramsCollectible.at(emograms_address)

        tokenIds = []
        for id in range(2, 101):
            owner = emograms.ownerOfById(id)
            print(id, owner)
            if owner == '0x0000000000000000000000000000000000000000':
                tokenIds.append(id)

        # Iterate over sell
        start = input("Ready to start sell transactions? (y/n)")
        for id in tokenIds:
            print(id, 1e18, d.tx_params)
            # tx_sell = marketplace.addEmogramToMarket(id, emograms, 1e18, d.tx_params)
