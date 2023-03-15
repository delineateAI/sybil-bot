from forta_agent import Finding, FindingType, FindingSeverity, get_json_rpc_url
from hexbytes import HexBytes
from web3 import Web3
import defaultdict
import logging

web3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))

known_airdrop_addresses = set()
num_transactions_contract_address = {}
known_ignore_list= set()
graph = defaultdict(dict)

##add to list
list_transfer_signatures = ["0xa9059cbb", "0x8abdfa02" ]

class Tree:
    def __init__(self, data):
        self.children = []
        self.data = data


def handle_transaction(w3, transaction_event):

    findings = []
    sender_address = transaction_event.from_
    erc20_address = transaction_event.to

    # Check if the token address is in the ignore list
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
    if function_signature in list_transfer_signatures:
        return findings

    # This is the address the token will be sent to by the token contract transfer function
    # right now we are assuming
    # need to figure out how to parse without the abi -- to get abi we need etherscan
    # TODO: See how to actually get argument (remove leading 0s)
    recipient_address = "0x" + transaction_data[10:74]

    # TODO: assure recipient address is NOT an exchange wallet!!!
    return checkSybil(recipient_address, erc20_address)


# check for sybil attacks given an airdrop from_address
# construct a graph of to_address transactions for every to_address
# see if there is any particular account that receives transfers from more than 5 to_addresses
def checkSybil(sender_address, erc20_address):

    # find all erc20_address transactions going TO the sender_address in the last week
    # start by pulling 50 transactions and then check the timestamp on the oldest

    # if more than 5 and less than 500, throw alert 
    return true
    # 500 is probably larger than any sybil attack, in which case its an exchange wallet
    return false
    

def is_eoa(w3: Web3, address: str) -> bool:
    """
    This function determines whether address is an EOA.
    Ethereum has two account types: Externally-owned account (EOA) – controlled by anyone with the private keys. Contract account – a smart contract deployed to the network, controlled by code.
    """
    if address is None:
        return False
    code = w3.eth.get_code(Web3.toChecksumAddress(address))
    return code == HexBytes("0x")

def initialize():
    # do some initialization on startup e.g. fetch data
    pass

def handle_block(block_event):
    findings = []
    # detect some block condition
    return findings

def handle_alert(alert_event):
    findings = []
    # detect some alert condition
    return findings
