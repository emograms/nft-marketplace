import scripts.polygon_mainnet_deploy as d
import json

with open('../latest_deployment.json', 'r') as deployments:
    addresses = json.load(deployments)
    marketplace_proxy_address = addresses['polygon-main']['PROXY']
    emograms_address = addresses['polygon-main']['EMOGRAMSCOLLECTIBLE']
    marketplace_address = addresses['polygon-main']['EMOGRAMMARKETPLACEUPGRADEABLE']
    DEPLOYER = '3365973dff537bf0899c163c867787afdbb5d368bea82d03d1d0fb299e53d15a'
    d.accounts.add(DEPLOYER)
    #  As there is already an account added in the script imported above, so I take the last element added
    DEPLOYER = d.accounts[-1]
    print('Loaded marketplace proxy at:', marketplace_proxy_address)
    print('Loaded emograms at:', emograms_address)
    print('Loaded deployer at:', DEPLOYER.address)


def main():
    # Setting gas fees
    d.set_gas(DEPLOYER)
    print('Transaction parameters to use:', d.tx_params)

    # Starting init
    start = input("Ready to start (y/n)")
    if start == 'y':
        emograms = d.EmogramsCollectible.at(emograms_address)
        marketplace = d.Contract.from_explorer(marketplace_proxy_address, as_proxy_for=marketplace_address)
        

        # Fetch emograms to sell
        tokenIds = []
        for id in range(2, 101):
            owner = emograms.ownerOfById(id)
            print(id, owner)
            if owner == '0x0000000000000000000000000000000000000000':
                tokenIds.append(id)

        # Iterate over sell
        print('List of emograms to put up on sale:')
        print(tokenIds)
        start = input("Ready to start sell transactions? (y/n)")
        for idx, id in enumerate(tokenIds):
            if idx < 3:
                x = input(f"{id}, 1e18, {d.tx_params}, \n")
                tx_sell = marketplace.addEmogramToMarket(
                    id, emograms, 1e18, d.tx_params)
            else:
                #  Avoid confirming transactions
                d.tx_params['required_confs'] = 0
                print(id, 1e18, d.tx_params)
                tx_sell = marketplace.addEmogramToMarket(
                    id, emograms, 1e18, d.tx_params)
                print(tx_sell)
