from forta_agent import Finding, FindingType, FindingSeverity, get_json_rpc_url
from hexbytes import HexBytes
from web3 import Web3
import logging


web3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))


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

    if not eoa_reciever:
        return findings
    # Get the input data of the transaction
    transaction_data = transaction_event.transaction.data
    # Return empty findings if the input data is empty
    if not transaction_data:
        return findings

    #Christian Way
    # First 4 bytes are the function selector
    # If the function signature is not "transfer(address,uint256)" or some ERC-20 equivalent, ignore the transaction
    function_signature = transaction_data[:10]
    if function_signature != "0xa9059cbb":
        return findings
    # Get the token address from the input data
    # The token address is the 21st to 40th characters of the input data
    token_address = "0x" + transaction_data[34:74]

    #Logan Way
    #ORRRR we may be able to get the token's address stright from from the input like Logan did on Alchemy
    #traces-> action -> call_type, input
    #the call_type could be a call, create, suicide, or reward
    #we want a call
    #but we still need to know if this is a Transfer function by checking the first 4 bytes
    #it could also be any
    # Check if the token address is in the ignore list
    if token_address in known_ignore_list:
        return findings



    #start building the graph starting with the reciever
    #add all the wallet adresses that sent the token in question to the reciever
    #keep building the graph by adding the wallet adresses that sent the token with depth of 5













# TODO: ask about
    # claim
    # etherscan api or keep track of transactions on our own
        # volume of transactions – feasible to keep in memory?
    # getting the token address from a transaction – is it the to_address?

'''
Is there a list of functions that we should be looking for as "claim" functions?
Do you think it'd be better to use an API to look at all transactions that involve a particular erc20 + recipient address while checking for a sybil attack? Or keep track of this information on our own?
How can we get the ERC20 token address from a transaction – would this just be the to_address in an airdrop claim?
'''

# check for sybil attacks given an airdrop from_address
# construct a graph of to_address transactions for every to_address
# see if there is any particular account that receives transfers from more than 5 to_addresses
def checkSybil(from_address):
    num_transfers_to = {}
    all_transfers = {} # TODO use etherscan api or keep track of this some other way
    # all_transfers = {34, 65}
    for to_address in all_transfers:
        all_transfers_from_to_address = {} # TODO use etherscan api or keep track of this some other way
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
    pass

def handle_block(block_event):
    findings = []
    # detect some block condition
    return findings

def handle_alert(alert_event):
    findings = []
    # detect some alert condition
    return findings
