import json, os, argparse, uuid, hashlib


"""
STEPS:

1. generate UUID for every tokenId (99 in total)
2. convert uuids to strings and store them in a file for later reference
3. hash the UUIDs using SHA256
4. Store the hashed strings in a file for later reference
5. set the desciption tag for each token with the associated UUID hash string

"""
hashes_str = []
uuids_obj = []
uuids_str = []

for x in range(0,101):
    uuids_obj.append(uuid.uuid4())
    uuids_str.append(str(uuids_obj[x]))
    hashes_str.append(hashlib.sha256(uuids_str[x].encode()).hexdigest())


file = open("/Users/patriko/Documents/GitHub/nft-marketplace/smart-contract/scripts/test/json_test.txt", 'r')
start = 2
external_url = "https://nft.emograms.com/emograms?id="
for lines in file:
    name = lines.split(" ")[0].strip()
    image = lines.split(" ")[1].strip()
    dictToWrite = {'name': name,
                   'image': image,
                   'description': hashes_str[start - 2],
                   'external_url': (external_url + str(start))}
    name = "JSONs_ID/" + str(start)
    start = start + 1               
    with open(name, "w") as write_file:
        json.dump(dictToWrite, write_file)
