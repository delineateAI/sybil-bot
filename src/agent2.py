from forta_agent import Finding, FindingType, FindingSeverity, get_json_rpc_url
from hexbytes import HexBytes
from web3 import Web3
import defaultdict
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

    # eoa_sender = is_eoa(w3, from_address)
    # eoa_reciever =  is_eoa(w3, to_address)
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
    # if not eoa_reciever:
    #     return findings

    # This is the address the token will be sent to by the token contract transfer function
    #right now we are assuming
    #need to figure out how to parse without the abi -- to get abi we need etherscan
    sending_token_to = "0x" + transaction_data[10:74]

    #start building the graph starting with the reciever
    #add all the wallet adresses that sent the token in question to the reciever
    # Set the list of wallet addresses to check to the receiver
    addresses_to_check = [(erc20_address, 0)]
    # Create a dictionary to store the graph
    graph = {}
    depth = 0
    while addresses_to_check:
        address, depth = addresses_to_check.pop(0)
        if address in known_airdrop_addresses or depth >= 5:
            continue
        known_airdrop_addresses.add(address)

        # Get all the transactions that involve the address whether sender or reciever
        #TODO: no idea how to get within last week without looking through block
        transactions = w3.eth.get_transactions(address)
        parent = Tree(address)
        children = []
        for tx_hash in transactions:
            # Get the transaction receipt
            tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
            #invalid transaction
            if not tx_receipt:
                continue
            #for each transaction find the sender's wallet address
            tx = w3.eth.get_transaction(tx_hash)
            sender_address = tx['from']
            # get_transactions does not care if address is the sender or reciever
            #so sender_address could have been reciever too
            if(sender_address == address):
                continue
            #add senders to graph
            #do we need to check if they sent a token
            addresses_to_check.append((sender_address, depth+1))
            # Get the input data of the transaction
            tx_data = tx_receipt["input"]
            if not tx_data:
                continue
            children.append(Tree(sender_address))
        parent.children = children







    # for i in range(depth):
    #     new_addresses_to_check = []
    #     for address in addresses_to_check:
    #         # Get the transactions for the address
    #         transactions = web3.eth.get_transaction_receipts(address)
    #         if transactions is None:
    #             continue
    #         # Check if any of the transactions are token transfers
    #         for transaction in transactions:
    #             # Get the input data of the transaction
    #             input_data = transaction.input
    #             # Get the first 10 characters of the input data to determine the function signature
    #             function_signature = input_data[:10]
    #             # If the function signature is "transfer(address,uint256)", check if the token address is the same as the one in question
    #             if function_signature == "0xa9059cbb":
    #                 transaction_token_address = "0x" + input_data[34:74]
    #                 if transaction_token_address == token_address:
    #                     # Get the wallet address the tokens were transferred to
    #                     to_address = "0x" + input_data[74:114]

    #                     # Add the transaction to the graph
    #                     if address in graph:
    #                         graph[address].append(to_address)
    #                     else:
    #                         graph[address] = [to_address]

    #                     # Add the to_address to the list of addresses to check in the next iteration
    #                     new_addresses_to_check.append(to_address)
    #     # Set the addresses_to_check to the new addresses to check for the next iteration
    #     addresses_to_check = new_addresses_to_check
    # # Print the final graph
    # print(graph)










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
