from constants import known_ignore_list
from forta_agent import Finding, FindingType, FindingSeverity, get_json_rpc_url
from hexbytes import HexBytes
from web3 import Web3
from datetime import datetime, timedelta
import logging
import requests


logging.basicConfig(filename='sybil.log', level=logging.DEBUG)


##TODO: does this web3 instacne change depending on the token being transacted??
w3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))

def is_exchange_wallet(wallet_address):
    url = f"https://api.forta.network/labels/state?sourceIds=etherscan,0x6f022d4a65f397dffd059e269e1c2b5004d822f905674dbf518d968f744c2ede&entities{wallet_address}=&labels=exchange"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if wallet_address in data and "labels" in data[wallet_address]:
            labels = data[wallet_address]["labels"]
            for label in labels:
                if label["label"] == "exchange" and label["confidence"] > 0.5:
                    return True
    return False

# add to list
#transfer, transferfrom, airdroptransfer
# transfer is used to transfer tokens from the caller's address to another address.
# It can only be called by the token owner, and the caller must have a sufficient balance to complete the transfer.

# transferFrom is used to transfer tokens from the address of an approved spender.
# It requires an extra step of approval, where the token owner must approve the spender address to
# make a transfer on their behalf using the approve method. The approved spender can then use transferFrom
# to transfer tokens from the token owner's address to another address.
# "0x8abdfa02" -- airdrop transfer function byt don't know how works
list_transfer_signatures = ["0xa9059cbb", "0x23b872dd" ]

transaction_count = {} # recipient_address: num_transactions
senders = {} #who is initiating these transactions to the recipient wallet

def analyze_transaction(w3, transaction_event):
    findings = []
    sender_address = transaction_event.from_
    erc20_address = transaction_event.to
    logging.debug(f"Transaction event {transaction_event.transaction.hash}")
    # Check if the token address is in the ignore list
    # anything that is not in known_ignore_list is an ongoing airdrop token
    # can we make this assumption that we
    if erc20_address in known_ignore_list:
        return findings

    # Get the input data of the transaction
    transaction_data = transaction_event.transaction.data

    # Return empty findings if the input data is empty
    if not transaction_data:
        return findings

    # First 4 bytes are the function selector
    # If the function signature is not "transfer(address,uint256)" or some ERC-20 equivalent, ignore the transaction
    function_signature = transaction_data[:10]
    if function_signature not in list_transfer_signatures:
        return findings

    logging.debug(f"Token Address {erc20_address}")
    # This is the address the token will be sent to by the token contract transfer function
    # right now we are assuming
    # need to figure out how to parse without the abi -- to get abi we need etherscan
    # int removes leading 0s if transaction_Data is a string
    logging.debug(f"Transaction data {transaction_data}")
    if function_signature == list_transfer_signatures[0]:
        #meaning transfer(address,uint256)
        recipient_address = "0x" + transaction_data[10:74].lstrip("0")
    else:
        #meaning transferFrom(address, address, uint256)
        from_address = "0x" + transaction_data[10:74].lstrip("0")
        recipient_address = "0x" + transaction_data[74:].lstrip("0")


    if erc20_address in transaction_count:
        #added extra check to make sure we increment count for every unqiue sender (airdrop 1000 fort and send many small transfers to recipinet wallet)
        senders[erc20_address][recipient_address].add(sender_address)
        if recipient_address in transaction_count[erc20_address]:
            #cannot make this an AND statement
            if(sender_address not in senders[erc20_address][recipient_address]):
                transaction_count[erc20_address][recipient_address] += 1
        else:
            transaction_count[erc20_address][recipient_address] = 1
            senders[erc20_address][recipient_address] = set(sender_address)

    else:
        transaction_count[erc20_address] = {recipient_address : 1}
        senders[erc20_address] = {recipient_address: set(sender_address)}

    # TODO: Check if exchange wallet
    # what alert id do we raise, severity, etc
    exchange_wallet = is_exchange_wallet(recipient_address)


    #Make sure that the To address should also not be a contract
    #does this mean make sure the reciever is EOA?

    #then what?

    #how should we determien confidence
    if transaction_count[erc20_address][recipient_address] == 6:
        findings.append( Finding({
        'name': 'Sybil Attack',
        'description': f'{recipient_address} wallet may be involved in a Sybil Attack for token {erc20_address}',
        'alert_id': 'AIRDROP-1',
        'labels': [
        {
            "entityType": EntityType.Address,
            "entity": f"{recipient_address}",
            "label": "Sybil; attacker wallet",
            "confidence": 0.7,
        }],
        'type': FindingType.Suspicious,
        'severity': FindingSeverity.Medium,
        'metadata': {
            "transaction_id": transaction_event.transaction.hash,
            'from': erc20_address,
            'to': recipient_address
        }}))
        logging.debug(f"Potential Sybil attack identified {findings}")

    return findings


# def find_block_timestamp(w3, event_block_number):
#     #need to change this to be whatever blockchain we are dealing with
#     event_block = w3.eth.getBlock(event_block_number)
#     timestamp = event_block.timestamp
#     timestamp_datetime = datetime.fromtimestamp(timestamp)
#     return timestamp_datetime


# check for sybil attacks given an airdrop from_address
# see if there is any particular account that receives transfers
# def checkSybil(w3, transaction_event, recipient_address, erc20_address):
#     # find all erc20_address transactions going TO the sender_address in the last week
#     # start by pulling 50 transactions and then check the timestamp on the oldest

#     # TODO: this probably needs to change. As it is right now, this looks at transfers IN THIS TRANSACTION only.
#     token_transfer_events = transaction_event.filter_log(ERC_20_TRANSFER_EVENT_ABI, erc20_address)

#     print(token_transfer_events)
#     # find all erc20_address transactions going FROM the erc20_address to sender_address in the last week
#     num_transactions = 0
#     week_ago = datetime.now() - timedelta(weeks=1)

#     # timestamp >= week_ago
#     for event in token_transfer_events:
#         logging.debug(f"Token Transfer Event  {event}")
#         timestamp = find_block_timestamp(w3, event.blockNumber)
#         if event['args']['from'] == erc20_address and \
#             event['args']['to'] == recipient_address:
#             num_transactions += 1

#     # [AttributeDict({'args': AttributeDict({'from': '0xf96cA963Fb2bE5c4eAF47C22c36cF2Fa26231e7f', 'to': '0xee9bd0E71681ee6E9Aa9F1ba46D2D1149f7BD054', 'value': 2000000000000000000000}), 'event': 'Transfer', 'logIndex': 26, 'transactionIndex': 9, 'transactionHash': '0x0afefa0d6262c4ef2bd22314647a8ad5b222bb8d3952780ca219849c826c0218', 'address': '0x41545f8b9472d758bb669ed8eaeeecd7a9c4ec29', 'blockHash': '0x580f931f76b7331e669958e0ddd5d43c283cb808792c868d638cee350223df60', 'blockNumber': 14971787})]

#     # if more than 5 and less than 500, throw alert
#     if num_transactions > 5 and num_transactions < 500:
#         return True
#     else:
#         # 500 is probably larger than any sybil attack, in which case its an exchange wallet
#         return False


def handle_transaction(transaction_event):
    # return real_handle_transaction(transaction_event)
    return analyze_transaction(w3, transaction_event)



