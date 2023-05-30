from .constants import known_ignore_list
from .L2_cache import L2Cache
from forta_agent import Finding, FindingType, FindingSeverity, get_json_rpc_url, EntityType
from hexbytes import HexBytes
from web3 import Web3
import datetime
import logging
import requests
import os


logging.basicConfig(filename='sybil.log', level=logging.DEBUG)

w3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))
CHAIN_ID = -1
senders = {} #who is initiating these transactions to the recipient wallet
last_clear =  datetime.datetime.now() # last clear
newlyDeployedContracts = {} #tokens that have been deployed
# Love token contract
# ["0xB22C05CeDbF879a661fcc566B5a759d005Cf7b4C"]
#once a deployed token gets its first transfer add it watchlist
watchlist = {}
# https://etherscan.io/address/0x4010ad9a0f67e26a85908e10f03de4b4d46c77f7#tokentxns <- test case
# test txs: 0x1a1c595d65129c4447ee128786a90f1a55f4a368a7ab17e4f9e5d069c2c91d59, 0x4464cc5a3adbdac655b175b2f9d78563e56cc3c7963350c8e2823eb2c2f73832, 0x964a3133da8e3ee68b7c18ad0b43010d5bc661d4217ded7b6ebdf07b9d64f4dc, 0x2017a1cc0ff5bce3b9ceb88cf0e432fb0ec07e11ac461ebd237233919c064949

# 0x28c6c06298d514db089934071355e5743bf21d60
# https://api.forta.network/labels/state?sourceIds=etherscan,0x6f022d4a65f397dffd059e269e1c2b5004d822f905674dbf518d968f744c2ede&entities={wallet_address}&labels=exchange
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

# # Token Age from first transfer
# TRANSFER_EVENT_SIGNATURE = 'Transfer(address,address,uint256)'
# def get_first_transfer(w3, token_address):
#     latest_block = w3.eth.blockNumber
#     transaction_receipt = w3.eth.getTransactionReceipt(token_address)
#     if transaction_receipt is not None:
#         contract_creation_block = transaction_receipt['blockNumber']
#     else:
#         return None
#     transfer_event_filter = w3.eth.filter({
#         'fromBlock': contract_creation_block,
#         'toBlock': latest_block,
#         'address': token_address,
#         'topics': [w3.keccak(text=TRANSFER_EVENT_SIGNATURE).hex()]
#     })
#     entries = transfer_event_filter.get_all_entries()
#     return entries[0] if entries else None

def is_token_older_than_6_months(w3, block_number):
    block = w3.eth.getBlock(block_number)
    block_time = datetime.utcfromtimestamp(block['timestamp'])
    now =  datetime.datetime.now()
    return (now - block_time) > datetime.timedelta(days=180)

def is_contract_deployment(transaction_event):
    # The 'to' field will be None for contract creation transactions
    if transaction_event['transaction']['to'] is None:
        return True
    else:
        return False

list_transfer_signatures = ["0xa9059cbb", "0x23b872dd" ]

def analyze_transaction(w3, transaction_event):
    global last_clear
    global CHAIN_ID
    if CHAIN_ID == -1:
        CHAIN_ID = w3.eth.chainId

    if(CHAIN_ID not in newlyDeployedContracts.keys()):
        newlyDeployedContracts[CHAIN_ID] = {}
    if(CHAIN_ID not in watchlist.keys()):
        watchlist[CHAIN_ID] = {}

    findings = []
    # Get the input data of the transaction
    transaction_data = transaction_event.transaction.data
    # Return empty findings if the input data is empty
    if not transaction_data:
        return findings
    #see if this transaction deploys a contract
    if is_contract_deployment(transaction_event):
        # WRONGGG transaction_event.contractAddress
        newlyDeployedContracts[CHAIN_ID].append( transaction_event.contractAddress )
        return findings

    # First 4 bytes are the function selector
    # If the function signature is not "transfer(address,uint256)" or some ERC-20 equivalent, ignore the transaction
    function_signature = transaction_data[:10]
    if function_signature not in list_transfer_signatures:
        return findings

    sender_address = transaction_event.from_
    erc20_address = transaction_event.to

    #if this transaction has 0 value, ignore
    if transaction_event.transaction.value <= 0:
        return findings

    # detect first transactions for recently deployed contracts and add to watchlist
    if erc20_address in newlyDeployedContracts[CHAIN_ID]:
        watchlist[CHAIN_ID].append(newlyDeployedContracts[CHAIN_ID].pop(erc20_address))

    # if a transaction is not a new token deployment or a transaction in our newly depoloyed list or our watchlist then ignore
    if erc20_address not in watchlist[CHAIN_ID]:
        return findings


    # at this point all txs will be nonzero, erc20 transfers on the watchlist of active recently created tokens

    if(CHAIN_ID not in senders.keys()):
        senders[CHAIN_ID] = {}
    logging.debug(f"Transaction event {transaction_event.transaction.hash}")
    # check if x days has passed since last clear and clear dictionary if necessary. Time window to assess concentration of token transactions
    if is_older_than_x_days(last_clear, 4):
        senders[CHAIN_ID].clear()
        last_clear = datetime.datetime.now()


    # if erc20_address in known_ignore_list:
    #     return findings

    #find the recipient if this transaciton a transfer
    logging.debug(f"Token Address {erc20_address}")
    logging.debug(f"Transaction data {transaction_data}")
    if function_signature == list_transfer_signatures[0]:
        #meaning transfer(address,uint256)
        recipient_address = "0x" + transaction_data[10:74].lstrip("0")
    else:
        #meaning transferFrom(address, address, uint256)
        recipient_address = "0x" + transaction_data[74:74+64].lstrip("0")

    #check if wallet an exchange or not EOA
    exchange_wallet = is_exchange_wallet(recipient_address)
    eoa = is_eoa(w3, recipient_address)
    if (exchange_wallet or not eoa):
        return findings

    # first_transfer = get_first_transfer(w3, erc20_address)
    # if erc20_address not in token_first_transfers.keys():
    #     token_first_transfers[erc20_address] = first_transfer
    # if is_token_older_than_6_months(w3, first_transfer['blockNumber']):
    #     return findings
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


    #if anyone is claiming more than their one airdrop for this new token, alert
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
            'watchlist_size': len(watchlist[CHAIN_ID])
        }}))
        logging.debug(f"Potential Sybil attack identified {findings}")

    return findings

