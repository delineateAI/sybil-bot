# Sybil Bot to Find Airdrop Hunters

## Description

Sybil attacks use a single network node to operate many fake identities, often simultaneously, within a Peer-to-Peer (P2P) network. A sybil attack leads to a small number of network actors gaining an undue share of influence, which in the context of an airdrop, means a larger share of governance tokens. However, intelligent anlayis of transaction history can reveal the wallet adresses behind these attacks and raise alerts when they have occured.  

## Supported Chains

- Ethereum

## Alerts

Describe each of the type of alerts fired by this agent

- FORTA-1
  - Fired when a transaction contains a Tether transfer over 10,000 USDT
  - Severity is always set to "low" (mention any conditions where it could be something else)
  - Type is always set to "info" (mention any conditions where it could be something else)
  - Mention any other type of metadata fields included with this alert

## Test Data

The agent behaviour can be verified with the following transactions:

- 0x3a0f757030beec55c22cbc545dd8a844cbbb2e6019461769e1bc3f3a95d10826 (15,000 USDT)
