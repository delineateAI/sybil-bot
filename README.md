# Sybil Bot to Find Airdrop Hunters

## Description

Sybil attacks use a single network node to operate many fake identities, often simultaneously, within a Peer-to-Peer (P2P) network. A sybil attack leads to a small number of network actors gaining an undue share of influence, which in the context of an airdrop, means a larger share of governance tokens. However, intelligent anlayis of transaction history can reveal the wallet adresses behind these attacks and raise alerts when they have occured.

## Supported Chains

- Omnichain

## Alerts

Describe each of the type of alerts fired by this agent

- SYBIL-1
  - Fired when a wallet recieves 6 transactions of an airdropped token
  - Severity is always set to medium
  - Type is always set to suspicious
  - METADATA
            "transaction_id":,
            "from":,
            'token_address':,
            'to':

## Test Data

The agent behaviour can be verified with the following transactions:

If the agent is not finding anything it is because the airdropped token value has gone to 0. 

npm run tx 0xc466958c04451fb29278b3e9d453b29308d7556b12e7706d7f9fe46e60a128e4,0x1a1c595d65129c4447ee128786a90f1a55f4a368a7ab17e4f9e5d069c2c91d59,0x4464cc5a3adbdac655b175b2f9d78563e56cc3c7963350c8e2823eb2c2f73832,0x964a3133da8e3ee68b7c18ad0b43010d5bc661d4217ded7b6ebdf07b9d64f4dc,0x2017a1cc0ff5bce3b9ceb88cf0e432fb0ec07e11ac461ebd237233919c064949"

