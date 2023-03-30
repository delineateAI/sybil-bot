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

npm run tx 0x338c6d7095228544f27ba8479aea6cadbe5aea98806a651f66ef30b3cd7e1813, 0x4e72d3fd19e0b4af0c7460d8ca8e6c97d6365d3015b87df0ce82448181e8dec4,0xc1251820fa0f60d5dfe8180f0096653ecf9300201e67698ab635fea6e10e4756,0xf525c43b707aae754eadafbfec8cc71799b02c2e976d12cc20e8686d558e74ad,0x1b5794f87eb5df64cd440de5b94fb226e999f7f279fe51a7f96e63f02676d24d,0x789a0ed195874b142acf5684fae10712c7770e35c14d8f9d8746d796e3fa1799,0x0a1942b33e33015fa948a2fd95ca8e77cdd3674837d14882daa91781bc46f007,0x3d012345a9702aae46e892e188a5365816834e277c171921c1d4f2145a1a447e,0xe154ded8c020cd84c3181ddb378b2cb82fbcdc7d6889255b950663913f1c1966,0x8761f1b009b5260e30561f611991b548072b9562bcc467987d6b96317ec912c1,0x528c515cc6671e8a3f76cebe51cea15b51e3994bdda6e99e3cbee816caf5025f,0xbd19d8f36c2cb274f34bcf678f63ffb4d8f41f9ebbd042a497e68041e4c59c66,0x0afefa0d6262c4ef2bd22314647a8ad5b222bb8d3952780ca219849c826c0218

