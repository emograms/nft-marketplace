import time
import random
from os import initgroups
import eth_utils
from brownie import *
import uuid, hashlib
from hexbytes import HexBytes

def encode_function_data(initializer=None, *args):
    """Encodes the function call so we can work with an initializer.
    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
        The initializer function we want to call. Example: `box.store`.
        Defaults to None.
        args (Any, optional):
        The arguments to pass to the initializer function
    Returns:
        [bytes]: Return the encoded bytes.
    """
    if len(args) == 0 or not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    else:
        return initializer.encode_input(*args)

# set up addresses, variables
# deploy contracts
# mint tokens, start initial auction
# upgrade to new contract
# check state variables
# continue init. auction on new contract
# check erc721 holding func.
# check sale of erc721
# check auction of erc721