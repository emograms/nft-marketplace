import json, os, argparse

file = open("/Users/patriko/Documents/GitHub/nft-marketplace/smart-contract/scripts/test/json_test.txt", 'r')
start = 2
for lines in file:
    name = lines.split(" ")[0].strip()
    image = lines.split(" ")[1].strip()
    dictToWrite = {'Name': name,
                   'image': image,
                   'description': ""}
    name = "JSONs_ID/" + str(start) + ".json"
    start = start + 1               
    with open(name, "w") as write_file:
        json.dump(dictToWrite, write_file)
