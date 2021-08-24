import os, argparse, ipfshttpclient


#Parsing the path
parser = argparse.ArgumentParser(description='Upload image and JSON files to IPFS')
parser.add_argument("--dir", metavar='D', help='the directory to upload as files', type=str)
args = parser.parse_args()

directory = args.dir

files_to_add = []
added = []

#Local Node Connection
IPFS_Host = '/ip4/127.0.0.1/tcp/8080'

for filename in os.scandir(directory):
    if filename.is_file():
        print(filename.path)
        files_to_add.append(filename.path)


try:
    api = ipfshttpclient.connect(addr=IPFS_Host)
    print(api)
except ipfshttpclient.exceptions.ConnectionError as ce:
    print(str(ce))

for filename in files_to_add:
    res = api.add(filename)
    added.append(res)

