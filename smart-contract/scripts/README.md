# deployment.py

The basic workflow for using the deployment script with Brownie:

 1. Open a in **repo/smart-contracts**`brownie console --network <network>`
 2. Import deployment script using `import scripts.deployment as d`
 3. It will load required wallets and you can set gas fees with `d.set_gas()`, which will ask for a gwei amount to be used with the deployment
 4. To deploy new contract instances use `emograms, proxy_marketplace, vault, marketplace = d.deploy_network(testMode=False, publishSource=True, saveJSON=True)`
 5. From now on you can use the returned `brownie.Contract` objects with further deployment functions or simply interact in brownie
 6. To mint the token use `d.mint_tokens(emograms, proxy_marketplace)` - this will create 1 of each `tokenId` and 110 of the SRT token (`tokenId=1)` to the address of the deployer
 7. In order to set originality hashes use `d.set_origin_hash(emograms)`
 8. To start the initial auction cycle and call `stepAuction()` function of the marketplace contract use `drun_initialAuction_cycles(emograms, marketplace, duration)` using duration as seconds if `testMode=True` and days if `testMode=True` during `d.deploy_network()`

### Other handful functionalities for console interaction

 - `emograms, marketplace, vault, proxy = d.load_deployed_contracts()` to load contracts instances from **repo/latest_deployment.json**
 - `d.distribute_ether(to, amount)` to manually send some ETH from the `DEPLOYER account`
