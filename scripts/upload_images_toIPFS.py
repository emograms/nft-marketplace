#imports
import json, ipfshttpclient, os, argparse

parser = argparse.ArgumentParser(description='Upload image and JSON files to IPFS')
parser.add_argument("--imgdir", metavar='D', help='the image directory to upload', type=str)
parser.add_argument("--jsondir", metavar='J', help='the directory to save the JSON files', type=str)
parser.add_argument("--ipfshost", metavar='H', help='Address of the IPFS Node', type=str)
parser.add_argument("--ipfsgateway", metavar='G', help='Address of IPFS Gateway e.g. Pinata', type=str)
args = parser.parse_args()

if(args.imgdir):
    IMG_DIR = args.imgdir
else:
    IMG_DIR = ''

if(args.jsondir):
    JSON_DIR = args.jsondir
else:
    JSON_DIR = ''

if(args.ipfshost):
    IPFS_HOST = args.ipfshost
else:
    IPFS_HOST = '<Multiaddr /dns/localhost/tcp/5001/http>'

if(args.ipfsgateway):
    IPFS_GATEWAY = args.ipfsgateway
else:
    IPFS_GATEWAY = "https://gateway.pinata.cloud/ipfs/"


ipfsClient = ipfshttpclient.connect(addr=IPFS_HOST)

#upload images
uploadedImages = ipfsClient.add(IMG_DIR, pattern='*.png', pin=True)
print("Files Uploaded: ")
print(uploadedImages)

#generate jsons
for files in uploadedImages:
    json_data = json.dumps({'name': files['Name'], 'image': IPFS_GATEWAY + files['Hash']})

    name = files['Name']
    name = name.split('.')
    path_to_file = JSON_DIR + name[0] + ".json"

    json_file = open(path_to_file, "w")
    json_file.write(json_data)
    json_file.close()
    
#upload jsons
uploadedJsons = ipfsClient.add(JSON_DIR, pattern="*.json", pin=True)

#return hashes
print(uploadedJsons)

#close connection
ipfsClient.close()