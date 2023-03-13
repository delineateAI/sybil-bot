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


known_airdrop_addresses = set()
num_transactions_contract_address = {}
known_ignore_list= set()

def handle_transaction(w3, transaction_event):

    findings = []
    from_address = transaction_event.from_
    to_address = transaction_event.to

    eoa_sender = is_eoa(w3, from_address)
    eoa_reciever =  is_eoa(w3, to_address)

    if not eoa_sender:
        # contract address sender, possibly an airdrop
        if from_address in known_airdrop_addresses:
            checkSybil(from_address)

        else:
            if from_address in num_transactions_contract_address:
                if num_transactions_contract_address[from_address] > 1000:
                    # more than 1000 accounts from this contract in the last x units of time, likely an airdrop
                    # TODO clear dictionary after x units of time
                    known_airdrop_addresses.add(from_address)
                    checkSybil(from_address)
                
            # check if claim function called
            erc20_token_address = to_address # (?)
            claim_function_abi = '{"name":"claim","type":"function","constant":false,"inputs":[TODO],"outputs":[TODO],"payable":false,"stateMutability":"nonpayable"}'
            claims = transaction_event.filter_function(claim_function_abi, erc20_token_address)
            if claims.length > 1:
                # airdrop claim found
                if from_address in num_transactions_contract_address:
                    num_transactions_contract_address[from_address] += 1
                else:
                    num_transactions_contract_address[from_address] = 1

    # skip if no EOAs involved in calling claim or recieving tokens
    if not (eoa_sender or eoa_reciever):
        return findings

    # return empty findings if empty transaction data?
    input_data = transaction_event.transaction.data
    if input_data is None:
        return findings


# check for sybil attacks given an airdrop from_address
# construct a graph of to_address transactions for every to_address
# see if there is any particular account that receives transfers from more than 5 to_addresses
def checkSybil(from_address):
    # TODO
    num_transfers_to = {}
    all_transfers = {} # TODO use etherscan api or keep track of this some other way
    for to_address in all_transfers:
        all_transfers_from_to_address = {} # TODO use etherscap api or keep track of this some other way
        for final_address in all_transfers_from_to_address:
            if final_address in num_transfers_to:
                num_transfers_to[final_address] += 1
            else:
                num_transfers_to[final_address] = 1
            if num_transfers_to[final_address] >= 5:
                # raise alert – sybil attack
                pass

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
