from .constants import known_ignore_list
from .L2_cache import L2Cache
from forta_agent import Finding, FindingType, FindingSeverity, get_json_rpc_url, EntityType
from hexbytes import HexBytes
from web3 import Web3
import datetime
import logging
import requests
import os
import rlp

#REmeber uncomment value if statement before submit

logging.basicConfig(filename='sybil.log', level=logging.DEBUG)

w3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))
CHAIN_ID = -1
SUPPORTED_CHAINS = [    1,
    56,
    137,
    43114,
    42161,
    10,
    250]

INITIALIZED = False

senders = {} #who is initiating these transactions to the recipient wallet
last_clear =  datetime.datetime.now() # last clear

NEWLY_DEPLOYED_CONTRACTS = {} #tokens that have been deployed
# Love token contract
# ["0xB22C05CeDbF879a661fcc566B5a759d005Cf7b4C"]
#once a deployed token gets its first transfer add it WATCHLIST
WATCHLIST = {}
# https://etherscan.io/address/0x4010ad9a0f67e26a85908e10f03de4b4d46c77f7#tokentxns <- test case
#  "npm run tx 0xc466958c04451fb29278b3e9d453b29308d7556b12e7706d7f9fe46e60a128e4,0x1a1c595d65129c4447ee128786a90f1a55f4a368a7ab17e4f9e5d069c2c91d59,0x4464cc5a3adbdac655b175b2f9d78563e56cc3c7963350c8e2823eb2c2f73832,0x964a3133da8e3ee68b7c18ad0b43010d5bc661d4217ded7b6ebdf07b9d64f4dc,0x2017a1cc0ff5bce3b9ceb88cf0e432fb0ec07e11ac461ebd237233919c064949"





def persist(obj: object, chain_id: int):
    L2Cache.write(obj, chain_id, chain_id)


def load(chain_id: int, key: str) -> object:
    return L2Cache.load(chain_id, chain_id)


def is_exchange_wallet(wallet_address):
    url = f"https://api.forta.network/labels/state?sourceIds=etherscan,0x6f022d4a65f397dffd059e269e1c2b5004d822f905674dbf518d968f744c2ede&entities={wallet_address}&labels=exchange"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["events"]
        for event in data:
            label = event["label"]
            if label["entity"] == wallet_address and label["confidence"] > 0.5:
                return True
    return False

def calc_contract_address(w3, address, nonce) -> str:
    """
    this function calculates the contract address from sender/nonce
    :return: contract address: str
    """

    address_bytes = bytes.fromhex(address[2:].lower())
    return w3.toChecksumAddress(w3.keccak(rlp.encode([address_bytes, nonce]))[-20:]).lower()

def is_contract_deployment(transaction_event):
    # The 'to' field will be None for contract creation transactions
    if transaction_event.transaction.to is None:
        return True
    else:
        return False

def is_older_than_x_days(last_check, x):
    time_diff = datetime.datetime.now() - last_check
    return time_diff.days >= x

def is_eoa(w3, address):
    """
    This function determines whether address is an EOA.
    Ethereum has two account types: Externally-owned account (EOA) – controlled by anyone with the private keys. Contract account – a smart contract deployed to the network, controlled by code.
    """
    if address is None:
        return False
    code = w3.eth.getCode(Web3.toChecksumAddress(address) )
    return not (len(code) > 2)


def initialize():
    """
    this function initializes the state variables that are tracked across tx and blocks
    it is called from test to reset state between tests
    """
    global INITIALIZED

    global NEWLY_DEPLOYED_CONTRACTS
    global WATCHLIST
    global CHAIN_ID
    for k in SUPPORTED_CHAINS:
        try:
            newly_deployed_contracts = load( CHAIN_ID, CHAIN_ID)
        except:
            newly_deployed_contracts = None
        NEWLY_DEPLOYED_CONTRACTS[k] = [] if newly_deployed_contracts is None else newly_deployed_contracts
    for k in SUPPORTED_CHAINS:
        try:
            watchlist = load( CHAIN_ID, CHAIN_ID)
        except:
            newly_deployed_contracts = None
        WATCHLIST[k] = [] if watchlist is None else watchlist

    INITIALIZED = True





list_transfer_signatures = ["0xa9059cbb", "0x23b872dd" ]

def analyze_transaction(w3, transaction_event):
    global last_clear
    global CHAIN_ID


    findings =[]
    if CHAIN_ID == -1:
        CHAIN_ID = w3.eth.chainId
    if(CHAIN_ID not in NEWLY_DEPLOYED_CONTRACTS.keys()):
        NEWLY_DEPLOYED_CONTRACTS[CHAIN_ID] = []
    if(CHAIN_ID not in WATCHLIST.keys()):
        WATCHLIST[CHAIN_ID] = []

    # Get the input data of the transaction
    transaction_data = transaction_event.transaction.data
    # Return empty findings if the input data is empty
    if not transaction_data:
        return findings
    #see if this transaction deploys a contract
    if is_contract_deployment(transaction_event):
        print("yo")
        NEWLY_DEPLOYED_CONTRACTS[CHAIN_ID].append(  calc_contract_address( w3, transaction_event.from_,  transaction_event.transaction.nonce ) )
        return findings



    # First 4 bytes are the function selector
    # If the function signature is not "transfer(address,uint256)" or some ERC-20 equivalent, ignore the transaction
    function_signature = transaction_data[:10]
    if function_signature not in list_transfer_signatures:
        return findings

    sender_address = transaction_event.from_
    erc20_address = transaction_event.to


    # if this transaction has 0 value, ignore
    # if transaction_event.transaction.value <= 0:
    #     return findings

    # detect first transactions for recently deployed contracts and add to WATCHLIST
    if erc20_address in NEWLY_DEPLOYED_CONTRACTS[CHAIN_ID]:
        NEWLY_DEPLOYED_CONTRACTS[CHAIN_ID].remove(erc20_address)
        WATCHLIST[CHAIN_ID].append(erc20_address)



    # if a transaction is not a new token deployment or a transaction in our newly depoloyed list or our WATCHLIST then ignore
    if erc20_address not in WATCHLIST[CHAIN_ID]:
        return findings

    # at this point all txs will be nonzero, erc20 transfers on the WATCHLIST of active recently created tokens
    if(CHAIN_ID not in senders.keys()):
        senders[CHAIN_ID] = {}

    # check if x days has passed since last clear and clear dictionary if necessary. Time window to assess concentration of token transactions
    if is_older_than_x_days(last_clear, 7):
        senders[CHAIN_ID].clear()
        last_clear = datetime.datetime.now()


    if function_signature == list_transfer_signatures[0]:
        #meaning transfer(address,uint256)
        recipient_address = "0x" + transaction_data[10:74].lstrip("0")
    else:
        #meaning transferFrom(address, address, uint256)
        from_address = "0x" + transaction_data[10:74].lstrip("0")
        recipient_address = "0x" + transaction_data[74:74+64].lstrip("0")

    # filter_out(recipient_address)
    # if should_filter(recipient_address):
    #     return findings

    # TODO: Check logic
    exchange_wallet = is_exchange_wallet(recipient_address)
    eoa = is_eoa(w3, recipient_address)
    if (exchange_wallet or not eoa):
        return findings



 #update the senders dictionary with new senders
    if erc20_address in senders[CHAIN_ID]:
        #added extra check to make sure we increment count for every unqiue sender (airdrop 1000 fort and send many small transfers to recipinet wallet)
        if recipient_address in senders[CHAIN_ID][erc20_address]:
            #cannot make this an AND statement
            senders[CHAIN_ID][erc20_address][recipient_address].add(sender_address)
        else:
            senders[CHAIN_ID][erc20_address][recipient_address] = {sender_address}

    else:
        senders[CHAIN_ID][erc20_address] = {recipient_address: {sender_address}}


    #TODO: how to increase confidence
    print(senders)
    if len( senders[CHAIN_ID][erc20_address][recipient_address]) == 2:
        findings.append( Finding({
        'name': 'Sybil Attack',
        'description': f'wallet {recipient_address} may be involved in a Sybil Attack for token {erc20_address}',
        'alert_id': 'SYBIL-1',
        'labels': [
        {
            "entityType": EntityType.Address,
            "entity": f"{recipient_address}",
            "label": "Sybil; attacker wallet",
            "confidence": 0.5,
        }],
        'type': FindingType.Suspicious,
        'severity': FindingSeverity.Medium,
        'metadata': {
            "transaction_id": transaction_event.transaction.hash,
            "wallet received tokens from the following addresses": list(senders[CHAIN_ID][erc20_address][recipient_address]),
            'token_address': erc20_address,
            'to': recipient_address,
            'watchlist_size': len(WATCHLIST[CHAIN_ID])
        }}))
        logging.debug(f"Potential Sybil attack identified {findings}")


        if datetime.datetime.now().minute == 0:  # every hour
            persist_state()


    return findings



def persist_state():
    global NEWLY_DEPLOYED_CONTRACTS
    global WATCHLIST
    global CHAIN_ID
    for k in NEWLY_DEPLOYED_CONTRACTS.keys():
        persist(NEWLY_DEPLOYED_CONTRACTS[k], CHAIN_ID, CHAIN_ID)
    for k in WATCHLIST.keys():
        persist(WATCHLIST[k], CHAIN_ID, CHAIN_ID)



def handle_transaction(transaction_event):
    # return real_handle_transaction(transaction_event)
    return analyze_transaction(w3, transaction_event)



