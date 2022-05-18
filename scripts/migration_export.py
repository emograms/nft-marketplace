import json
from brownie import EmogramsCollectible, EmogramMarketplaceUpgradeable, ERC1967Proxy, network, Contract

networkName = network.show_active()
print("Active Network: ")
print(networkName + "\n")

with open('latest_deployment.json', 'r') as f:
    data = json.load(f)
    f.close()

emograms_address = data[networkName]['EMOGRAMSCOLLECTIBLE']
marketplace_address = data[networkName]['EMOGRAMMARKETPLACEUPGRADEABLE']
proxy_address = data[networkName]['PROXY']

emograms = EmogramsCollectible.at(emograms_address)
marketplace = EmogramMarketplaceUpgradeable.at(proxy_address)


def main():

    emogramsTokenOwners = {}
    maxEmogramNum = emograms.maxEmogramNum()

    # Get NFTs
    print('NFT export started...')
    for i in range(2,101):
        emogramsTokenOwners[i] = emograms.ownerOfById(i)
    print('NFT export finished!')

    # Get SRT
    print('SRT export started...')
    srtBalances = {}
    for i in range(maxEmogramNum):
        if emogramsTokenOwners[i] != '0x0000000000000000000000000000000000000000':
            srtBalances[emogramsTokenOwners[i]] = emograms.balanceOf(
                emogramsTokenOwners[i], 1)

    print('SRT export finished!')

    # Get Marketplace data - fixed price
    print('Fixed price export started...')
    emogramsOnSale = {}
    emogramsOnSaleLenght = marketplace.emogramsOnSaleLength()
    for i in range(emogramsOnSaleLenght):
        emogramsOnSale[i] = marketplace.emogramsOnSale(i)
    print('Fixed price export finished!')

    # Get Marketplace data - auction
    print('Auction export started...')
    emogramsOnAuction = {}
    emogramsOnAuctionLenght = marketplace.emogramsOnAuctionLength()
    for i in range(emogramsOnAuctionLenght):
        emogramsOnAuction[i] = marketplace.emogramsOnAuction(i)
    print('Auction export finished!')

    # print('Printing results:...')
    # print('Emogram NFT Token owners JSON:')
    # print(emogramsTokenOwners)
    # print('\nEmogram SRT Token owners JSON:')
    # print(srtBalances)
    # print('\nEmograms for sale on marketplace JSON:')
    # print(emogramsOnSale)
    # print('\nEmograms for auction on marketplace JSON:')
    # print(emogramsOnAuction)

    data = {
        'NFTOwners': emogramsTokenOwners,
        'SRTOwners': srtBalances,
        'EmogramsOnSale': emogramsOnSale,
        'EmogramsOnAuction': emogramsOnAuction
    }
    export_file = str(network.show_active()) + '_export.json'
    with open(export_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print('Export finished! File saved at: ', export_file)
