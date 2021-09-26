

# deployment.py

The basic workflow for using the deployment script with Brownie:

 1. Open a in **repo/smart-contracts**`brownie console --network=<goerli/mainnet>`
 2. Import deployment script using `import scripts.deployment as d`
 3. It will load required wallets and you can set gas fees with `d.set_gas()`, which will ask for a gwei amount to be used with the deployment
 4. To deploy new contract instances use `emograms, proxy_marketplace, vault, marketplace = d.deploy_network(testMode=False, publishSource=True, saveJSON=True)`
 6. If Etherscan verification fails try again with eg.: `EmogramMarketplaceUpgradeable.publish_source(marketplace, silent=False)`
 7. To mint the token use `d.mint_tokens(emograms)` - this will create 1 of each `tokenId` and 110 of the SRT token (`tokenId=1)` to the address of the deployer
 8. In order to set originality hashes use `d.set_origin_hash(emograms)`
 9. To start the initial auction cycle and call `stepAuction()` function of the marketplace contract use `d.run_initialAuction_cycles(emograms, marketplace, duration)` using duration as seconds if `testMode=True` and days if `testMode=True` during `d.deploy_network()`

### Other handful functionalities for console interaction

 - `emograms, marketplace, vault, proxy = d.load_deployed_contracts()` to load contracts instances from **repo/latest_deployment.json**
 - `distribute_ether_from_deployer(to, amount)` to manually send some ETH from the `DEPLOYER account`

### Itearte over an initial auction from script
After deploying the contracts and minting tokens using the previous methods use this simple loop to iterate over the initial auction 33 day cycle.
```
>>> from time import sleepa
>>>  AUCTION_PERIOD_SEC = 55
>>> for i in range(34):
...     d.run_initialAuction_cycles(emograms, marketplace, AUCTION_PERIOD_SEC)
...     sleep(AUCTION_PERIOD_SEC + 5)
```
### Full deployment code - ONLY FOR GOERLI

**IMPORTANT NOTE:**
If you want to deploy to `mainnet` use `testMode=True` for `d.deploy_network(...)` step.

**Example code for GOERLI:**
```
brownie console --network=goerli

Brownie v1.16.3 - Python development framework for Ethereum

SmartContractProject is the active project.
Brownie environment is ready.
>>> import scripts.deployment as d

----- Deployment script loaded -----
Active Network: 
goerli

Wallet addreses used:
MIKI:     0xFe594E862c3ce76E192997EABFC41Afd7C975b52
CSONGOR:  0x76cA42252508c0AD52bf7936dC3eabb82cF9872e
PATR:     0xE7E8FB1932084E3BbE382EbaCdc16D835B30216F
ADR:      0xA558c9148846F17AcD9E99D8a8D0D1ECdCf0c7fA
DEPLOYER: 0xb501ec584f99BD7fa536A8a83ebCf413282193eb

Use set_gas() before interacting!
>>> d.set_gas()
Please set an EIP1559 priority fee (gwei):150
Gas prices set at:  150  gwei
>>> emograms, proxy_marketplace, vault, marketplace = d.deploy_network(testMode=True, publishSource=True, saveJSON=True)
Transaction sent: 0xd791fcb886402019796e9770ad67672ff255960ac92cd008d22467a00c9e57e0
  Max fee: 150.000000014 gwei   Priority fee: 150.0 gwei   Gas limit: 6022372   Nonce: 654
  EmogramsCollectible.constructor confirmed   Block: 5561620   Gas used: 5474884 (90.91%)   Gas price: 150.000000007 gwei
  EmogramsCollectible deployed at: 0xFe5f161279333f2d14e73851bcF3d743B5775680

Waiting for https://api-goerli.etherscan.io/api to process contract...
Verification submitted successfully. Waiting for result...
Verification pending...
Verification pending...
Verification complete. Result: Pass - Verified
Transaction sent: 0x3adb57d332fea6875a11cc07fa522fb312df6d42276fded1eb9be687ca3ceb48
  Max fee: 150.000000014 gwei   Priority fee: 150.0 gwei   Gas limit: 5302983   Nonce: 655
  EmogramMarketplaceUpgradeable.constructor confirmed   Block: 5561625   Gas used: 4820894 (90.91%)   Gas price: 150.000000007 gwei
  EmogramMarketplaceUpgradeable deployed at: 0x4085b5600260a04006d5ba44d24A1cB1B346f311

Waiting for https://api-goerli.etherscan.io/api to process contract...
Verification submitted successfully. Waiting for result...
Verification pending...
Verification complete. Result: Pass - Verified
Transaction sent: 0x5f106972b95c06951b80a82aafd8a71cf34b3e8ea6acb3a2356f11b806e3e41d
  Max fee: 150.000000014 gwei   Priority fee: 150.0 gwei   Gas limit: 271406   Nonce: 656
  ERC1967Proxy.constructor confirmed   Block: 5561629   Gas used: 246733 (90.91%)   Gas price: 150.000000007 gwei
  ERC1967Proxy deployed at: 0x5F28b0A1111fb66c52ed8c8288ee87142A55b955

Waiting for https://api-goerli.etherscan.io/api to process contract...
Verification submitted successfully. Waiting for result...
Verification pending...
Verification complete. Result: Pass - Verified
Transaction sent: 0x3cbb6618db62fc39eff46fc5899406af462c3cb8df94eee14fd82f6a8e96fec4
  Max fee: 150.000000014 gwei   Priority fee: 150.0 gwei   Gas limit: 245712   Nonce: 657
  Transaction confirmed   Block: 5561634   Gas used: 218142 (88.78%)   Gas price: 150.000000007 gwei

Transaction sent: 0xdaba138ac710c483c29dce6d22397c4a783391714ef841759f55552cbec08a16
  Max fee: 150.000000014 gwei   Priority fee: 150.0 gwei   Gas limit: 1604358   Nonce: 658
  FounderVault.constructor confirmed   Block: 5561637   Gas used: 1458508 (90.91%)   Gas price: 150.000000007 gwei
  FounderVault deployed at: 0x3783434f72736bf32957539a86154B371531d25A

Waiting for https://api-goerli.etherscan.io/api to process contract...
Verification submitted successfully. Waiting for result...
Verification complete. Result: Pass - Verified
Contracts deployed on: goerli
Transaction sent: 0x2f9d1f84514ae4f7e2962326a95871d433ac51ec4ada64ab136bd2f0cd01ae86
  Max fee: 150.000000014 gwei   Priority fee: 150.0 gwei   Gas limit: 33475   Nonce: 659
  EmogramsCollectible.setBeneficiary confirmed   Block: 5561641   Gas used: 30432 (90.91%)   Gas price: 150.000000007 gwei

Transaction sent: 0x1e5e6af336a27df5e4fdf20e4f201876e4ecd3883941b8f0fc8b02412f567f2b
  Max fee: 150.000000014 gwei   Priority fee: 150.0 gwei   Gas limit: 2530046   Nonce: 660
  Transaction confirmed   Block: 5561642   Gas used: 2264773 (89.52%)   Gas price: 150.000000007 gwei

Transaction sent: 0x8d52e073ce0113ea1a7defc032159db39647f1b9ed38df2f3c46b5e55c92e426
  Max fee: 150.000000014 gwei   Priority fee: 150.0 gwei   Gas limit: 126468   Nonce: 661
  EmogramsCollectible.setURI confirmed   Block: 5561643   Gas used: 114971 (90.91%)   Gas price: 150.000000007 gwei

Transaction sent: 0x47559db5b42b1e3498f04fc3828dfedd39cbdfd1ec603485e609be16255d39bd
  Max fee: 150.000000014 gwei   Priority fee: 150.0 gwei   Gas limit: 63242   Nonce: 662
  EmogramsCollectible.setApprovalForAll confirmed   Block: 5561645   Gas used: 57493 (90.91%)   Gas price: 150.000000007 gwei

Deployment JSON loaded from latest_deployment.json for overwriting: 
 {'goerli': {'EMOGRAMMARKETPLACEUPGRADEABLE': '0x6D5C620251B8AA21E6C25bC52e3157AdA664f47C', 'EMOGRAMSCOLLECTIBLE': '0x598cc2DECc906B6177371AED42272D94B8876562', 'FOUNDERVAULT': '0x65fd7D4b28a341AeCE65181Ee6F5Dd9734f12131', 'PROXY': '0x12a2C84B85FC5b01df9A2999aBA2159cbB41fC14'}}
>>> d.mint_tokens(emograms, proxy_marketplace)
Transaction sent: 0xf5ead5a5b02b2baba58505d2fb797ec02c3151c77efcc306b7de56eaa02cea85
  Max fee: 150.000000014 gwei   Priority fee: 150.0 gwei   Gas limit: 2643880   Nonce: 663
  EmogramsCollectible.mintBatch confirmed   Block: 5561671   Gas used: 2403528 (90.91%)   Gas price: 150.000000007 gwei

Total emograms minted:  209
>>> d.set_origin_hash(emograms)
Transaction sent: 0x2a17310634d399f1504a3503dcffa00702f5086e5455c690fd47f2128aaa0ce9
  Max fee: 150.000000014 gwei   Priority fee: 150.0 gwei   Gas limit: 2517401   Nonce: 664
  EmogramsCollectible.setOrigHash confirmed   Block: 5561673   Gas used: 2288547 (90.91%)   Gas price: 150.000000007 gwei

# If you like to iterate over the whole auction
>>> from time import sleep
>>>  AUCTION_PERIOD_SEC = 55
>>> for i in range(34):
...     d.run_initialAuction_cycles(emograms, proxy_marketplace, AUCTION_PERIOD_SEC)
...     sleep(AUCTION_PERIOD_SEC + 5)
Auction cycle #1  Start price:  1e+17
Transaction sent: 0xeacd64694eeff962d8d07d975f0dd75207faa426522cdbf1bb9ac1b5e2cc3035
  Max fee: 150.000000014 gwei   Priority fee: 150.0 gwei   Gas limit: 877747   Nonce: 665
  Transaction confirmed   Block: 5561679   Gas used: 777539 (88.58%)   Gas price: 150.000000007 gwei

and so on ....
``` 
