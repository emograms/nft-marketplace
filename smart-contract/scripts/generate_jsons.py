import json, os, argparse, uuid, hashlib
from hexbytes import HexBytes
from os import walk
import time
from os import listdir
from os.path import isfile, join

def merge_JsonFiles():
    result = list()
    for x in range(1,100):
        fileToOpen = "/Users/patriko/Documents/GitHub/nft-marketplace/smart-contract/scripts/JSONs_ID/" + str(x)
        with open(fileToOpen, 'r') as infile:
            with open('JSONs_ID/0', 'a') as output_file:
                output_file.write(str(json.load(infile)) + "\n")

hashes_str = []
uuids_obj = []
uuids_str = []
uuids_bytes = []

for x in range(0,101):
    uuids_obj.append(uuid.uuid4())
    uuid_string = str(uuids_obj[x]).replace('-', '')
    uuids_str.append(HexBytes(uuid_string).hex())
    hashes_str.append(hashlib.sha256(uuids_str[x].encode()).hexdigest())
    uuids_bytes.append(bytes(hashes_str[x], 'UTF-8'))

file = open("/Users/patriko/Documents/GitHub/nft-marketplace/smart-contract/scripts/test/json_test.txt", 'r')

SRT_im_link = "https://cloudflare-ipfs.com/ipfs/QmcBY2e46AjygK4eQGbXthdddtLSexc5s86Sz7iN1ZiSfh"
SRT_Dict = {'name': "SRT",
            'image': SRT_im_link,
            'description': "Each Emogram NFT comes with one special Sculpture Redemption Token (SRT). There will be only 99 of these tokens, and no new tokens will be minted at any time. Owners of the specific emogram NFTs can burn 11 of these SRT tokens to redeem a physical sculpture of the specific Emogram NFT. Buyers would only be able to redeem the sculpture if they are the owner of the specific NFT. Users are able to buy just the SRT tokens, without the NFT, but the only use case for these tokens are the redemption of the sculptures.",
            'external_url': "nft.emograms.com"}

with open("JSONs_ID/1", "w") as write_file:
    json.dump(SRT_Dict, write_file)

start = 2
external_url = "https://nft.emograms.com/emograms?id="
for lines in file:
    name = lines.split(" ")[0].strip()
    image = lines.split(" ")[1].strip()
    dictToWrite = {'name': name,
                   'image': image,
                   'description': hashes_str[start - 1],
                   'external_url': (external_url + str(start))}
    name = "JSONs_ID/" + str(start)
    start = start + 1               
    with open(name, "w") as write_file:
        json.dump(dictToWrite, write_file)
file.close()

file = open("/Users/patriko/Documents/GitHub/nft-marketplace/smart-contract/scripts/test/json_test.txt", 'r')
start = 0
for lines in file:
    name = lines.split(" ")[0].strip()
    name2 = "JSONs_UUID/" + name + ".json"
    start = start + 1
    with open(name2, "w") as write_file:
        write_file.write(name + ": " + uuids_str[start] + " hash: " + hashes_str[start])


time.sleep(3)

merge_JsonFiles()
