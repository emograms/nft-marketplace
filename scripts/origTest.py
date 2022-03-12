import uuid, hashlib
from hexbytes import HexBytes

hashes_str = []
uuids_obj = []
uuids_str = []

for x in range(0,101):
    uuids_obj.append(uuid.uuid4())
    uuid_string = str(uuids_obj[x]).replace('-', '')
    uuids_str.append(uuid_string)
    hashes_str.append(hashlib.sha256(uuids_str[x].encode()).hexdigest())

emograms = EmogramsCollectible.deploy({'from': accounts[0]})
marketplace = EmogramMarketplaceUpgradeable.deploy({'from': accounts[0]})
marketplace.initialize(True, {'from': accounts[0]})

emograms.setOrigHash(hashes_str)

emograms.originalityHash(2)
hashes_str[0]
hashlib.sha256(uuids_str[0].encode()).hexdigest()
emograms.verifyOrig(bytes(uuids_str[0], 'UTF-8'), 2).return_value