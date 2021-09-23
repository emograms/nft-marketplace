import json, os, argparse

file = open("/Users/patriko/Documents/GitHub/nft-marketplace/smart-contract/scripts/test/json_test.txt", 'r')
start = 2
for lines in file:
    name = lines.split(" ")[0].strip()
    image = lines.split(" ")[1].strip()
    dictToWrite = {'name': name,
                   'image': image,
                   'external_url': "https://nft.emograms.com/emograms?id=" + str(start),
                   'description': ""}
    name = "JSONs_ID/" + str(start)
    start = start + 1               
    with open(name, "w") as write_file:
        json.dump(dictToWrite, write_file)
