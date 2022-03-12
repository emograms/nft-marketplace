import json, os, argparse, uuid, hashlib
from hexbytes import HexBytes
from os import walk
import time
from os import listdir
from os.path import isfile, join

json_new_names = []

path = "/Users/patriko/Documents/GitHub/nft-marketplace/smart-contract/scripts/JSONs_ID_hex/"
files = os.listdir(path)

for x in range (0,101):
    json_new_names.append(str(hex(x))[2:].zfill(64))

for x in range(0,101):
    os.rename(path+str(x), path+json_new_names[x])

