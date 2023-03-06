from forta_agent import Finding, FindingType, FindingSeverity, get_json_rpc_url
from hexbytes import HexBytes
from web3 import Web3
import logging


web3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))

ERC20_TRANSFER_EVENT = '{"name":"Transfer","type":"event","anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}]}'
TETHER_ADDRESS = '0xdAC17F958D2ee523a2206206994597C13D831ec7'
TETHER_DECIMALS = 6
findings_count = 0

def is_eoa(w3: Web3, address: str) -> bool:
    """
    This function determines whether address is an EOA.
    Ethereum has two account types: Externally-owned account (EOA) – controlled by anyone with the private keys. Contract account – a smart contract deployed to the network, controlled by code.
    """
    if address is None:
        return False
    code = w3.eth.get_code(Web3.toChecksumAddress(address))
    return code == HexBytes("0x")


# def tx_data_to_text(w3, data: str):
#     try:
#         text = w3.toText(data).strip()
#         text_count = text.split(" ")
#         if len(text_count) >= MIN_TOKEN_COUNT:
#             return text
#     except Exception as err:
#         # logger.warning(f"Failed parsing tx data: {err}")
#         return None



def handle_transaction(w3, transaction_event):

    ##TRANSACTION FLOW over time
        #no clue yet how to do this -- read papers

    ##AIRDROP CLAIM
    #so we are getting any transaction in a block
    #this transaction could be a token airdrop transfer meaning from a token's smart contract to an EOA (externally owned account)
        #how do we know it it is an airdrop transaction? What are the identifying features
            #should we make a list of known token contract addresses on Ethereum ?
    # |
    # | these steps may be both a part of determining if its an airdrop transaction
    # |
    #IF this is indeed something to do with an airdrop
        #look for EOA calling claim function OR
        #EOA recieving a lot of tokens in this transaction

    #find claim function in signature hash
        #once you have a human readable function using rainbow table check to see if in list of airdrop functions
        # use below to monitor this function or something idk
        #https://github.com/arbitraryexecution/forta-bot-templates/tree/main/src/monitor-function-calls (can be used to find function calls to a contract)



    #so we know this is an airdrop claim transaction and we know which functions have been called in the token contract
        #from this determine the chances this is an airdrop hunter (size trasnaction, other features -- LOT OF WORK HERE)

    # -- can we use other forta bots to analyze wallets/transaction flowas over time/ect?


    findings = []
    from_address = transaction_event.from_
    to_address = transaction_event.to

    #find out if this is a token airdrop trasnaction of some sort


    eoa_sender = is_eoa(w3, from_address)
    eoa_reciever =  is_eoa(w3, to_address)

    # skip if no EOAs involved in calling claim or recieving tokens
    if not (eoa_sender or eoa_reciever):
        return findings

    # return empty findingss if empty transaction data?
    input_data = transaction_event.transaction.data
    if input_data is None:
        return findings


    #see if the transaction was signed by a token contract function like claim



    #we want to look at map of all addresses involved most liley
    addresses = transaction_event.addresses





    #to filter and decode function calls in the transaction or traces
    erc20_token_address = '0x123abc'
    transfer_event_abi = '{"name":"Transfer","type":"event","anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}]}'
    transfers = transaction_event.filter_log(transfer_event_abi, erc20_token_address)
    print(f'found {transfers.length} transfer events')


    # # limiting this agent to emit only 5 findings so that the alert feed is not spammed
    # global findings_count
    # if findings_count >= 5:
    #     return findings

    # # filter the transaction logs for any Tether transfers
    # tether_transfer_events = transaction_event.filter_log(
    #     ERC20_TRANSFER_EVENT, TETHER_ADDRESS)

    # for transfer_event in tether_transfer_events:
    #     # extract transfer event arguments
    #     to = transfer_event['args']['to']
    #     from_ = transfer_event['args']['from']
    #     value = transfer_event['args']['value']
    #     # shift decimals of transfer value
    #     normalized_value = value / 10 ** TETHER_DECIMALS

    #     # if more than 10,000 Tether were transferred, report it
    #     if normalized_value > 10000:
    #         findings.append(Finding({
    #             'name': 'High Tether Transfer',
    #             'description': f'High amount of USDT transferred: {normalized_value}',
    #             'alert_id': 'FORTA-1',
    #             'severity': FindingSeverity.Low,
    #             'type': FindingType.Info,
    #             'metadata': {
    #                 'to': to,
    #                 'from': from_,
    #             }
    #         }))
    #         findings_count += 1

    # return findings

def initialize():
    # do some initialization on startup e.g. fetch data

def handle_block(block_event):
    findings = []
    # detect some block condition
    return findings

def handle_alert(alert_event):
    findings = []
    # detect some alert condition
    return findings
