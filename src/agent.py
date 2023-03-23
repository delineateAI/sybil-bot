from forta_agent import Finding, FindingType, FindingSeverity, get_json_rpc_url
from hexbytes import HexBytes
from web3 import Web3
from datetime import datetime, timedelta
import logging
logging.basicConfig(filename='sybil.log', level=logging.DEBUG)
ERC_20_TRANSFER_EVENT_ABI = '{"name":"Transfer","type":"event","anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}]}'
ERC_20_TRANSFER_FROM_FUNCTION_ABI = '{"name":"transferFrom","type":"function","constant":false,"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"outputs":[],"payable":false,"stateMutability":"nonpayable"}'

w3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))

known_airdrop_addresses = set()
num_transactions_contract_address = {}
known_ignore_list= set()

##add to list
list_transfer_signatures = ["0xa9059cbb", "0x8abdfa02" ]


def analyze_transaction(w3, transaction_event):
    findings = []
    sender_address = transaction_event.from_
    erc20_address = transaction_event.to
    logging.debug(f"Transaction event {transaction_event.transaction.hash}")

    print("hi")
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
    if function_signature not in list_transfer_signatures:
        return findings

    logging.debug(f"Token Address {erc20_address}")
    # This is the address the token will be sent to by the token contract transfer function
    # right now we are assuming
    # need to figure out how to parse without the abi -- to get abi we need etherscan
    # int removes leading 0s if transaction_Data is a string
    logging.debug(f"Transaction data {transaction_data}")
    recipient_address = "0x" + transaction_data[10:74].lstrip("0")

    # TODO: Check if exchnage wallet (isn't this the if check in the sybil attack func)
    #what alert id do we raise, severity, ect
    if(checkSybil(w3, transaction_event, recipient_address, erc20_address)):
        findings.append( Finding({
        'name': 'Sybil Attack',
        'description': f'{recipient_address} wallet may be involved in a Sybil Attack for token {erc20_address}',
        'alert_id': 'FORTA-7',
        'type': FindingType.Info,
        'severity': FindingSeverity.Info,
        'metadata': {
            "transaction_id": transaction_event.transaction.hash,
            'from': erc20_address,
            'to': recipient_address
        }}))
        logging.debug(f"Potential Sybil attck identified {findings}")
    return findings


def find_block_timestamp(w3, event_block_number):
    #need to change this to be whatever blockchain we are dealing with
    event_block = w3.eth.getBlock(event_block_number)
    timestamp = event_block.timestamp
    timestamp_datetime = datetime.fromtimestamp(timestamp)
    return timestamp_datetime


# check for sybil attacks given an airdrop from_address
# see if there is any particular account that receives transfers
def checkSybil(w3, transaction_event, recipient_address, erc20_address):
    # find all erc20_address transactions going TO the sender_address in the last week
    # start by pulling 50 transactions and then check the timestamp on the oldest
    token_transfer_events = transaction_event.filter_log(ERC_20_TRANSFER_EVENT_ABI, erc20_address)
    # find all erc20_address transactions going FROM the erc20_address to sender_address in the last week
    num_transactions = 0
    week_ago = datetime.now() - timedelta(weeks=1)

    # timestamp >= week_ago
    for event in token_transfer_events:
        logging.debug(f"Token Transfer Event  {event}")
        timestamp = find_block_timestamp(w3, event.blockNumber)
        if event['args']['from'] == erc20_address and \
            event['args']['to'] == recipient_address :
            num_transactions += 1

    # if more than 5 and less than 500, throw alert
    if num_transactions > 5 and num_transactions < 500:
        return True
    else:
        # 500 is probably larger than any sybil attack, in which case its an exchange wallet
        return False


def provide_handle_transaction(w3):
    def handle_transaction(transaction_event):
        return analyze_transaction(w3, transaction_event)

    return handle_transaction


real_handle_transaction = provide_handle_transaction(w3)


def handle_transaction(transaction_event):
    return real_handle_transaction(transaction_event)


#TEST#
# npm run tx 0x4e72d3fd19e0b4af0c7460d8ca8e6c97d6365d3015b87df0ce82448181e8dec4,0xc1251820fa0f60d5dfe8180f0096653ecf9300201e67698ab635fea6e10e4756,0xf525c43b707aae754eadafbfec8cc71799b02c2e976d12cc20e8686d558e74ad,0x1b5794f87eb5df64cd440de5b94fb226e999f7f279fe51a7f96e63f02676d24d,0x789a0ed195874b142acf5684fae10712c7770e35c14d8f9d8746d796e3fa1799,0x0a1942b33e33015fa948a2fd95ca8e77cdd3674837d14882daa91781bc46f007,0x3d012345a9702aae46e892e188a5365816834e277c171921c1d4f2145a1a447e,0xe154ded8c020cd84c3181ddb378b2cb82fbcdc7d6889255b950663913f1c1966,0x8761f1b009b5260e30561f611991b548072b9562bcc467987d6b96317ec912c1,0x528c515cc6671e8a3f76cebe51cea15b51e3994bdda6e99e3cbee816caf5025f,0xbd19d8f36c2cb274f34bcf678f63ffb4d8f41f9ebbd042a497e68041e4c59c66,0x0afefa0d6262c4ef2bd22314647a8ad5b222bb8d3952780ca219849c826c0218

# def is_eoa(w3: Web3, address: str) -> bool:
#     """
#     This function determines whether address is an EOA.
#     Ethereum has two account types: Externally-owned account (EOA) – controlled by anyone with the private keys. Contract account – a smart contract deployed to the network, controlled by code.
#     """
#     if address is None:
#         return False
#     code = w3.eth.get_code(Web3.toChecksumAddress(address))
#     return code == HexBytes("0x")

# def initialize():
#     # do some initialization on startup e.g. fetch data
#     pass

# def handle_block(block_event):
#     findings = []
#     # detect some block condition
#     return findings

# def handle_alert(alert_event):
#     findings = []
#     # detect some alert condition
#     return findings
