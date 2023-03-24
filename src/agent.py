from forta_agent import Finding, FindingType, FindingSeverity, get_json_rpc_url
from hexbytes import HexBytes
from web3 import Web3
from datetime import datetime, timedelta
import logging
logging.basicConfig(filename='sybil.log', level=logging.DEBUG)
#TODO: make a constants file
ERC_20_TRANSFER_EVENT_ABI = '{"name":"Transfer","type":"event","anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}]}'
ERC_20_TRANSFER_FROM_FUNCTION_ABI = '{"name":"transferFrom","type":"function","constant":false,"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"outputs":[],"payable":false,"stateMutability":"nonpayable"}'


##TODO: does this web3 instacne change depending on the token being transacted??
w3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))

alerts_thrown = set()
# ['Tether', 'USD Coin', 'Binance USD', 'Shiba Inu', 'Dai', 'Uniswap', 'Wrapped Bitcoin', 'Chainlink', 'UNUS SED LEO', 'OKB', 'Aptos', 'TrueUSD', 'Lido DAO', 'Cronos', 'Arbitrum', 'ApeCoin', 'Quant', 'The Graph', 'Decentraland', 'BitDAO', 'Aave', 'Immutable', 'Axie Infinity', 'The Sandbox', 'Pax Dollar', 'KuCoin Token', 'Chiliz', 'Rocket Pool', 'Optimism', 'USDD', 'Curve DAO Token', 'Synthetix', 'PancakeSwap', 'Maker', 'GMX', 'Gemini Dollar', 'BitTorrent(New)', 'Frax Share', 'SingularityNET', 'GateToken', 'Huobi Token', 'PAX Gold', 'Trust Wallet Token', 'Loopring', 'Mask Network', 'Render Token', 'THORChain', '1inch Network', 'Fei USD', 'Convex Finance', 'dYdX', 'Nexo', 'Enjin Coin', 'Kava', 'Basic Attention Token', 'Threshold', 'ssv.network', 'MAGIC', 'WOO Network', 'Oasis Network', 'Balancer', 'FLOKI', 'Ankr', 'Holo', 'Compound', 'yearn.finance', 'Injective', 'Gnosis', 'Gala', 'Ethereum Name Service', 'Audius', 'OMG Network', 'Bone ShibaSwap', 'STEPN', 'Golem', 'SushiSwap', 'Blur', 'JUST', 'JasmyCoin', 'Ocean Protocol', 'DAO Maker', 'Band Protocol', 'Liquity', 'MX TOKEN', '0x', 'Livepeer', 'Biconomy', 'Celer Network', 'Bitgert', 'Dogelon Mars', 'Reserve Rights', 'SwissBorg', 'aelf', 'SKALE', 'iExec RLC', 'Alchemy Pay', 'Keep Network', 'BinaryX', 'BORA', 'Amp', 'SafePal', 'Polymath', 'Illuvium', 'SPACE ID', 'Storj', 'JOE', 'Multichain', 'UMA', 'RSK Infrastructure Framework', 'Gitcoin', 'Synapse', 'Braintrust', 'API3', 'MetisDAO', 'Axelar', 'HEX', 'Lido Staked ETH', 'T-mac DAO', 'Bitcoin BEP2', 'Wrapped BNB', 'Huobi BTC', 'Frax', 'BitTorrent', 'Bitget Token', 'Tether Gold', 'FTX Token', 'NXM', 'USDJ', 'Liquity USD', 'Gains Network', 'Baby Doge Coin', 'Astrafer', 'Edgecoin', 'GensoKishi Metaverse', 'Wrapped Everscale', 'Artificial Liquid Intelligence', 'inSure DeFi', 'LUKSO', 'STASIS EURO', 'Telcoin', 'OriginTrail', 'Hashflow', 'Tribe', 'PlayDapp', 'VVS Finance', 'Ribbon Finance', 'Pundi X (New)', 'Smooth Love Potion', 'Kyber Network Crystal v2', 'ConstitutionDAO', 'Chromia', 'Stargate Finance', 'APENFT', 'Merit Circle', 'MARBLEX', 'renBTC', 'Dent', 'Cocos-BCX', 'Status', 'Numeraire', 'Civic', 'Onyxcoin', 'Ren', 'Venus USDC', 'DeXe', 'Cartesi', 'Vulcan Forged PYR', 'Locus Chain', 'Request', 'Galxe', 'NYM', 'Ontology Gas', 'Aragon', 'Augur', 'STP', 'MVL', 'Voyager Token', 'NuCypher', 'Morpheus.Network', 'Bancor', 'Prom', 'Orbs', 'dKargo', 'Humanscape', 'MOBOX', 'DODO', 'Dusk Network', 'Powerledger', 'Celsius', 'TrueFi', 'VeThor Token', 'Alpha Venture DAO', 'tomiNet', 'AVINOC', 'Volt Inu V2', 'WINkLink', 'Function X', 'Saitama', 'Marlin', 'IQ', 'XCAD Network', 'Metal DAO', 'Metars Genesis', 'Loom Network', 'Covalent', 'Vibing', 'Aura Finance', 'Spell Token', 'MyNeighborAlice', 'Mdex', 'FUNToken', 'Highstreet', 'Rally', 'CEEK VR', 'Sologenic', 'Bifrost', 'LooksRare', 'Venus', 'Veritaseum', 'Wrapped NXM', 'Pendle', 'Dejitaru Tsuka', 'Alien Worlds', 'World Mobile Token', 'QuarkChain', 'Biswap', 'Ultra', 'Verasity', 'XYO', 'Grove Coin', 'WazirX', 'RACA', 'Orbit Chain', 'Yield Guild Games', 'cVault.finance', 'Sun (New)', 'Orchid', 'Perpetual Protocol', 'Origin Protocol', 'LCX', 'Venus BUSD', 'Beta Finance', 'Automata Network', 'XSGD', 'RichQUACK.com', 'Badger DAO', 'Ankr Staked ETH', 'StormX', 'Vega Protocol', 'Mines of Dalarnia', 'Aavegotchi', 'RSS3', 'Hifi Finance (Old)', 'Vai', 'Toko Token', 'Dawn Protocol', 'Linear Finance', 'NEST Protocol', 'Aergo', 'Strike', 'ARPA', 'SOMESING', 'NvirWorld', 'Ampleforth', 'Cobak Token', 'MXC', 'Seedify.fund', 'MovieBloc', 'Persistence', 'Ampleforth Governance Token', 'Gods Unchained', 'Rakon', 'Utrust', 'Coin98', 'Gifto', 'Efinity Token', 'Chainbing', 'Clash of Lilliput', 'SelfKey', 'SuperVerse', 'Alpaca Finance', 'smARTOFGIVING', 'Bloktopia', 'Raydium', 'QuickSwap', 'Lyra', 'KLAYswap Protocol', 'FirmaChain', 'DeFi Pulse Index', 'Shiba Predator', 'Uquid Coin', 'Flamingo', 'Enzyme', 'Kepple', 'DFI.Money', 'sUSD', 'HUNT', 'Polkastarter', 'Carry', 'Litentry', 'Revain', 'ZEON', 'SuperRare', 'Virtua', 'UFO Gaming', 'Celo Dollar', 'Star Atlas DAO', 'Hifi Finance', 'Velo', 'Measurable Data Token', 'SingularityDAO', 'Moss Coin', 'Beefy Finance', 'DeGate', 'Opulous', 'League of Kingdoms Arena', 'Gelato', 'DXdao', 'BABB', 'Propy', 'Defigram', 'Alchemix', 'TrustSwap', 'Zebec Protocol', 'Sweat Economy', 'Wilder World', 'BakeryToken', 'Neopin', 'FC Barcelona Fan Token', 'Bounce Governance Token', 'Nine Chronicles', 'IDEX', 'Wirex Token', 'Gas', 'NuNet', 'Keep3rV1', 'RAMP', 'Origin Dollar', 'SONM (BEP-20)', 'Hourglass', 'Star Atlas', 'DIA', 'Alpha Quark Token']

known_ignore_list = ['0xdac17f958d2ee523a2206206994597c13d831ec7', '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', 'BUSD-BD1', '0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce', '0x6b175474e89094c44da98b954eedeac495271d0f', '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984', '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599', '0x514910771af9ca656af840dff83e8264ecf986ca', '0x2af5d2ad76741191d15dfe7bf6ac92d4bd912ca3', '0x75231f58b43240c9718dd58b4967c5114342a86c', '0x1::aptos_coin::AptosCoin', '0x0000000000085d4780B73119b644AE5ecd22b376', '0x5a98fcbea516cf06857215779fd812ca3bef1b32', '0xa0b73e1ff0b80914ab6fe0444e65848c4c34450b', '0x912CE59144191C1204E64559FE8253a0e49E6548', '0x4d224452801aced8b2f0aebe155379bb5d594381', '0x4a220e6096b25eadb88358cb44068a3248254675', '0xc944e90c64b2c07662a292be6244bdf05cda44a7', '0x0f5d2fb29fb7d3cfee444a200298f468908cc942', '0x1A4b46696b2bB4794Eb3D4c26f1c55F9170fa4C5', '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9', '0xf57e7e7c23978c3caec3c3548e3d615c346e79ff', '0xbb0e17ef65f82ab018d8edd776e8dd940327b28b', '0x3845badAde8e6dFF049820680d1F14bD3903a5d0', '0x8e870d67f660d95d5be530380d0ec0bd388289e1', '0xf34960d9d60be18cc1d5afc1a6f012a723a28811', '0x3506424f91fd33084466f402d5d97f05f8e3b4af', '0xd33526068d116ce69f19a9ee46f0bd304f21a51f', '0x4200000000000000000000000000000000000042', '0x0c10bf8fcb7bf5412187a595ab97a3609160b5c6', '0xD533a949740bb3306d119CC777fa900bA034cd52', '0xc011a73ee8576fb46f5e1c5751ca3b9fe0af2a6f', '0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82', '0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2', '0xfc5a1a6eb076a2c7ad06ed22c90d7e710e35ad0a', '0x056Fd409E1d7A124BD7017459dFEa2F387b6d5Cd', 'TAFjULxiVgT4qWk6UZwjqwZXTSaGaqnVp4', '0x3432b6a60d23ca0dfca7761b7ab56459d9c964d0', '0x5B7533812759B45C2B44C19e320ba2cD2681b542', '0xe66747a101bff2dba3697199dcce5b743b454759', '0x6f259637dcd74c767781e37bc6133cd6a68aa161', '0x45804880de22913dafe09f4980848ece6ecbaf78', '0x4b0f1812e5df2a09796481ff14017e6005508003', '0xbbbbca6a901c926f240b89eacb641d8aec7aeafd', '0x69af81e73a73b40adf4f3d4223cd9b1ece623074', '0x6de037ef9ad2725eb40118bb1702ebb27e4aeb24', 'RUNE-B1A', '0x111111111117dc0aa78b770fa6a738034120c302', '0x956F47F50A910163D8BF957Cf5846D573E7f87CA', '0x4e3fbd56cd56c3e72c1403e103b45db9da5b9d2b', '0x92d6c1e31e14520e676a687f0a93788b716beff5', '0xb62132e35a6c13ee1ee0f84dc5d40bad8d815206', '0xf629cbd94d3791c9250152bd8dfbdf380e2a3b9c', '0x0C356B7fD36a5357E5A017EF11887ba100C9AB76', '0x0d8775f648430679a709e98d2b0cb6250d2887ef', '0xCdF7028ceAB81fA0C6971208e83fa7872994beE5', '0x9D65fF81a3c488d585bBfb0Bfe3c7707c7917f54', '0x539bdE0d7Dbd336b79148AA742883198BBF60342', '0x4691937a7508860f876c9c0a2a617e7d9e945d4b', '0x26B80FBfC01b71495f477d5237071242e0d959d7', '0xba100000625a3754423978a60c9317c58a424e3D', '0xcf0c122c6b73ff809c693db761e7baebe62b6a2e', '0x8290333cef9e6d528dd5618fb97a76f268f3edd4', '0x6c6ee5e31d828de241282b9606c8e98ea48526e2', '0xc00e94cb662c3520282e6f5717214004a7f26888', '0x0bc529c00c6401aef6d220be8c6ea1667f6ad93e', '0xe28b3b32b6c345a34ff64674606124dd5aceca30', '0x6810e776880c02933d47db1b9fc05908e5386b96', '0x15D4c048F83bd7e37d49eA4C83a07267Ec4203dA', '0xC18360217D8F7Ab5e7c516566761Ea12Ce7F9D72', '0x18aaa7115705e8be94bffebde57af9bfc265b998', '0xd26114cd6ee289accf82350c8d8487fedb8a0c07', '0x9813037ee2218799597d83D4a5B6F3b6778218d9', '0x3019BF2a2eF8040C242C9a4c5c4BD4C81678b2A1', '0x7DD9c5Cba05E151C895FDe1CF355C9A1D5DA6429', '0x6b3595068778dd592e39a122f4f5a5cf09c90fe2', '0x5283d291dbcf85356a21ba090e6db59121208b44', 'TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9', '0x7420B4b9a0110cdC71fB720908340C03F9Bc03EC', '0x967da4048cd07ab37855c090aaf366e4ce1b9f48', '0x0f51bb10119727a7e5ea3538074fb341f56b09ad', '0xba11d00c5f74255f56a5e366f4f77f5a186d7f55', '0x6DEA81C8171D0bA574754EF6F8b412F2Ed88c54D', '0x11eef04c884e24d9b7b4760e7476d06ddf797f36', '0xe41d2489571d322189246dafa5ebde1f4699f498', '0x58b6a8a3302369daec383334672404ee733ab239', '0xf17e65822b568b3903685a7c9f496cf7656cc6c2', '0x4f9254c83eb525f9fcf346490bbb3ed28a81c667', '0x8fff93e810a2edaafc326edee51071da9d398e83', '0x761d38e5ddf6ccf6cf7c55759d5210750b5d60f3', '0x320623b8e4ff03373931769a31fc52a4e78b5d70', '0xba9d4199fab4f26efe3551d490e3821486f135ba', '0xbf2179859fc6D5BEE9Bf9158632Dc51678a4100e', '0x00c83aecc790e8a4453e5dd3b0b4b3680501a7a7', '0x607f4c5bb672230e8672085532f7e901544a7375', '0xed04915c23f00a313a544955524eb7dbd823143d', '0x85eee30c52b0b379b046fb0f85f4f3dc3009afec', '0x5b1f874d0b0C5ee17a495CbB70AB8bf64107A3BD', '0x02cbe46fb8a1f579254a9b485788f2d86cad51aa', '0xff20817765cb7f73d4bde2e66e067e58d11095c2', '0xd41fdb03ba84762dd66a0af1a6c8540ff1ba5dfb', '0x9992ec3cf6a55b00978cddf2b27bc6882d88d1ec', '0x767fe9edc9e0df98e07454847909b5e959d7ca0e', '0x2dfF88A56767223A5529eA5960Da7A3F5f766406', '0xb64ef51c888972c908cfacf59b47c1afbc0ab8ac', '0x6e84a6216eA6dACC71eE8E6b0a5B7322EEbC0fDd', '0x65ef703f5594d2573eb71aaf55bc0cb548492df4', '0x04Fa0d235C4abf4BcF4787aF4CF447DE572eF828', '0x2acc95758f8b5f583470ba265eb685a8f45fc9d5', '0xde30da39c46104798bb5aa3fe8b9e0e1f348163f', '0x0f2D719407FdBeFF09D87557AbB7232601FD9F29', '0x799ebfabe77a6e34311eeee9825190b9ece32824', '0x0b38210ea11411557c13457D4dA7dC6ea731B88a', '0x9E32b13ce7f2E80A01932B42553652E053D6ed8e', '0x467719aD09025FcC6cF6F8311755809d45a5E5f3', '0x2b591e99afe9f32eaa6214f7b7629768c40eeb39', '0xae7ab96520de3a18e5e111b5eaab095312d7fe84', '0x71b87be9ccBABe4F393e809dfc26Df3c9720E0a2', 'BTCB-1DE', '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c', '0x0316EB71485b0Ab14103307bf65a021042c6d380', '0x853d955acef822db058eb8505911ed77f175b99e', '1002000', '0x19de6b897ed14a376dda0fe53a5420d2ac828a28', '0x68749665FF8D2d112Fa859AA293F07A622782F38', 'FTT-F11', '0xd7c49cee7e9188cca6ad8ff264c1da2e69d4cf3b', 'TMwFHYXLJaRUPeW6421aqXL4ZEzPRFGkGT', '0x5f98805A4E8be255a32880FDeC7F6728C6568bA0', '0xE5417Af564e4bFDA1c483642db72007871397896', '0xAC57De9C1A09FeC648E93EB98875B212DB0d460B', '0x97Bbbc5d96875fB78D2F14b7FF8d7a3a74106F17', 'GB7XD6DHWS45C3H7PQ25PSRFQB2QFPLMW4JZH4L7CU4O5NFE42MNNUSE', '0xAE788F80F2756A86aa2F410C651F2aF83639B95b', '0:a49cd4e158a9a15555e624759e2e4e766d22600b7800d891e46f9291f044a93d', '0x6b0b3a982b4634ac68dd83a4dbf02311ce324181', '0xcb86c6a22cb56b6cf40cafedb06ba0df188a416e', '0xA8b919680258d369114910511cc87595aec0be6D', '0xdb25f211ab05b1c97d595516f45794528a807ad8', '0x467bccd9d29f223bce8043b84e8c8b282827790f', '0xaa7a9ca87d3694b5755f213b5d04094b8d0f0a6f', '0xb3999F658C0391d94A37f7FF328F3feC942BcADC', '0xc7283b66Eb1EB5FB86327f08e1B5816b0720212B', '0x3a4f40631a4f906c2BaD353Ed06De7A5D3fCb430', '0x839e71613f9aA06E5701CF6de63E303616B0DDE3', '0x6123b0049f904d730db3c36a31167d9d4121fa6b', '0x0fd10b9899882a6f2fcb5c371e17e70fdee00c38', '0xCC8Fa225D80b9c7D42F96e9570156c65D6cAAa25', '0xdeFA4e8a7bcBA345F687a2f1456F5Edd9CE97202', '0x7a58c0be72be218b41c608b7fe7c5bb630736c71', '0x8a2279d4a90b6fe1c4b30fa660cc9f926797baa2', '0xaf5191b0de278c7286d6c7cc6ab6bb8a73ba2cd6', '0x198d14f2ad9ce69e76ea330b374de4957c3f850a', '0x949d48eca67b17269629c7194f4b727d4ef9e5d6', '0xd068c52d81f4409b9502da926ace3301cc41f623', '0xeb4c2781e4eba804ce9a9803c67d0893436bb27d', '0x3597bfd533a99c9aa083587b074434e61eb0a258', '0xc4c7ea4fab34bd9fb9a5e1b1a98df76e26e6407c', '0x744d70fdbe2ba4cf95131626614a1763df805b9e', '0x1776e1F26f98b1A5dF9cD347953a26dd3Cb46671', '0x41e5560054824ea6b0732e656e3ad64e20e94e45', '0xA2cd3D43c775978A96BdBf12d733D5A1ED94fb18', '0x408e41876cccdc0f92210600ef50372656052a38', '0xeca88125a5adbe82614ffc12d0db554e2e2867c8', '0xde4EE8057785A7e8e800Db58F9784845A5C2Cbd6', '0x491604c0fdf08347dd1fa4ee062a822a5dd06b5d', '0x430ef9263e76dae63c84292c3409d61c598e9682', '0xc64500dd7b0f1794807e67802f8abbf5f8ffb054', '0x8f8221afbb33998d8584a2b05749ba73c37a938a', '0x5fAa989Af96Af85384b8a938c2EdE4A7378D9875', '0x525A8F6F3Ba4752868cde25164382BfbaE3990e1', '0x308bfaeAaC8BDab6e9Fc5Ead8EdCb5f95b0599d9', '0xa117000000f279d81a1d3cc75430faa017fa5a2e', '0x1985365e9f78359a9B6AD760e32412f4a445E862', '0xde7d85157d9714eadf595045cc12ca4a5f3e2adb', '0xa849eaae994fb86afa73382e9bd88c2b6b18dc71', '0x3C4B6E6e1eA3D4863700D7F76b36B7f3D3f13E3d', '0x4fe83213d56308330ec302a8bd641f1d0113a4cc', '0xd3E4Ba569045546D09CF021ECC5dFe42b1d7f6E4', '0x1f573d6fb3f13d689ff844b4ce37794d79a7ff1c', '0xfc82bb4ba86045af6f327323a46e80412b91b27d', '0xff56cc6b1e6ded347aa0b7676c85ab0b3d08b0fa', '0x5dc60C4D5e75D22588FA17fFEB90A63E535efCE0', '0x07327a00ba28D413f745C931bbe6bE053B0AD2a6', '0x3203c9e46ca618c8c1ce5dc67e7e9d75f5da2377', '0x43dfc4159d86f3a37a5a4b3d4580b888ad7d4ddd', '0x940a2db1b7008b6c776d4faaca729d6d4a4aa551', '0x595832f8fc6bf59c85c527fec3740a1b7a361269', '0xaaaebe6fe48e54f431b0c390cfaf0b017d09d42d', '0x4c19596f5aaff459fa38b0f7ed92f11ae6543784', '0x0000000000000000000000000000456E65726779', '0xa1faa113cbe53436df28ff0aee54275c13b40975', '0x4385328cc4d643ca98dfea734360c0f596c83449', '0xf1ca9cb74685755965c7458528a36934df52a3ef', '0x7db5af2b9624e1b3b4bb69d6debd9ad1016a58ac', 'TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7', '0x8c15ef5b4b21951d50e53e4fbda8298ffad25057', '0xce3f08e664693ca792cace4af1364d5e220827b2', '0x57b946008913b82e4df85f501cbaed910e58d26c', '0x579cea1889991f68acc35ff5c3dd0621ff29b0c9', 'zil1z5l74hwy3pc3pr3gdh3nqju4jlyp0dzkhq2f5y', '0xF433089366899D83a9f26A773D59ec7eCF30355e', '0x238d02ee3f80fbf5e381f049616025c186889b68', '0x42476F744292107e34519F9c357927074Ea3F75D', '0xD417144312DbF50465b1C641d016962017Ef6240', '0x756176aff6b885eD0C21B1718c739bF8A371eF82', '0xc0c293ce456ff0ed870add98a0828dd4d2903dbf', '0x090185f2135308bad17527004364ebcc2d37e5f6', '0xAC51066d7bEC65Dc4589368da368b212745d63E8', '0x25d2e80cb6b86881fd7e07dd263fb79f4abe033c', '0x419d0d8bdd9af5e606ae2232ed285aff190e711b', '0x71Ab77b7dbB4fa7e017BC15090b2163221420282', '0xf1f955016EcbCd7321c7266BccFB96c68ea5E49b', '0xb056c38f6b7dc4064367403e26424cd2c60655e1', '0xc2c28b58db223da89b567a0a98197fc17c115148', '0x0c7D5ae016f806603CB1782bEa29AC69471CAb9c', '0xf4d2888d29d722226fafa5d9b24f9164c092421e', '0xcf6bb5389c92bdda8a3747ddb454cb7a64626c63', '0x8f3470A7388c05eE4e7AF3d01D8C722b0FF52374', '0x0d438f3b5175bebc262bf23753c1e53d03432bde', '0x808507121b80c02388fad14726482e061b8da827', '0xc5fb36dd2fb59d3b98deff88425a3f425ee469ed', '0x888888848B652B3E3a0f34c96E00EEC0F3a23F72', '1d7f33bd23d85e1a25d87d86fac4f199c3197a2f7afeb662a0f34e1e776f726c646d6f62696c65746f6b656e', '0xea26c4ac16d4a5a106820bc8aee85fd0b7b2b664', '0x965f527d9159dce6288a2219db51fc6eef120dd1', '0xd13c7342e1ef687c5ad21b27c2b65d772cab5c8c', '0xf411903cbc70a74d22900a5de66a2dda66507255', '0x55296f69f40ea6d20e478533c15a6b08b654e758', '0xf33893de6eb6ae9a67442e066ae9abd228f5290c', 'WRX-ED1', '0x12BB890508c125661E03b09EC06E404bc9289040', '0x662b67d00a13faf93254714dd601f5ed49ef2f51', '0x25f8087ead173b73d6e8b84329989a8eea16cf73', '0x62359ed7505efc61ff1d56fef82158ccaffa23d7', 'TSSMHYeV2uE9qYH95DqyoCuNCzEL1NvU3S', '0x4575f41308EC1483f3d399aa9a2826d74Da13Deb', '0xbc396689893d065f41bc2c6ecbee5e0085233447', '0x8207c1ffc5b6804f6024322ccf34f29c3541ae26', '0x037a54aab062628c9bbae1fdb1583c195585fe41', '0x95c78222B3D6e262426483D42CfA53685A67Ab9D', '0xbe1a001fe942f96eea22ba08783140b9dcc09d28', '0xa2120b9e674d3fc3875f415a7df52e382f141225', '0x70e8de73ce538da2beed35d14187f6959a8eca96', '0xD74b782E05AA25c50e7330Af541d46E18f36661C', '0x3472a5a71965499acd81997a54bba8d852c6e53d', '0xe95a203b1a91a908f9b9ce46459d101078c2c3cb', '0xa62cc35625b0c8dc1faea39d33625bb4c15bd71c', '0xcb84d72e61e383767c4dfeb2d8ff7f4fb89abc6e', '0x081131434f93063751813c619ecca9c4dc7862a3', '0x3F382DbD960E3a9bbCeaE22651E88158d2791550', '0xc98d64da73a6616c42117b582e832812e7b8d57f', '0xdf2c7238198ad8b389666574f2d8bc411a4b7428', '0x4bd17003473389a42daf6a0a729f6fdb328bbbd7', '0x9f589e3eabe42ebc94a44727b3f3531c0c877809', '0x580c8520deda0a441522aeae0f9f7a5f29629afa', '0x3e9bc21c9b189c09df3ef1b824798658d5011937', '0x04abeda201850ac0124161f037efd70c74ddc74c', 'AERGO-46B', '0x74232704659ef37c08995e386a2e26cc27a8d7b1', '0xba50933c268f567bdc86e1ac131be072c6b0b71a', '0xdcd62c57182e780e23d2313c4782709da85b9d6c', '0x9d71CE49ab8A0E6D2a1e7BFB89374C9392FD6804', '0xd46ba6d942050d489dbd938a2c909a5d5039a161', '0xD85a6Ae55a7f33B0ee113C234d2EE308EdeAF7fD', '0x5ca381bbfb58f0092df149bd3d243b08b9a8386e', '0x477bc8d23c634c154061869478bce96be6045d12', 'e5a49d7fd57e7178e189d3965d1ee64368a1036d', 'IBC/A0CC0CF735BFB30E730C70019D4218A1244FF383503FF7579C9201AB93CA9293', '0x77fba179c79de5b7653f68b5039af940ada60ce0', '0xccc8cb5229b0ac8069c51fd58367fd1e622afd97', '0x6e5a43db10b04701385a34afb670e404bc7ea597', '0xdc9Ac3C20D1ed0B540dF9b1feDC10039Df13F99c', '0xae12c5930881c53715b369cec7606b70d8eb229f', '0x72fF5742319eF07061836F5C924aC6D72c919080', '0x656C00e1BcD96f256F224AD9112FF426Ef053733', '0x1900E8B5619a3596745F715d0427Fe617c729BA9', '0x9ce116224459296abc7858627abd5879514bc629', '0x4cc19356f2d37338b9802aa8e8fc58b0373296e7', '0xe53ec727dbdeb9e2d5456c3be40cff031ab40a55', '0x8f0528ce5ef7b51152a59745befdd91d97091d2f', '0x8578530205cecbe5db83f7f29ecfeec860c297c2', '0xA0d96fD642156FC7E964949642257b3572f10cD6', '0x5245c0249e5eeb2a0838266800471fd32adb1089', '0x6c28aef8977c9b773996d0e8376d2ee379446f2f', '0x01ba67aac7f75f647d94220cc98fb30fcc5105bf', '0xc6a2ad8cc6e4a7e08fc37cc5954be07d499e7654', '0xe1bad922f84b198a08292fb600319300ae32471b', '0x1494ca1f11d487c2bbe4543e90080aeba4ba3c2b', '0xa71d0588EAf47f12B13cF8eC750430d21DF04974', '0x8806926ab68eb5a7b909dcaf6fdbe5d93271d6e2', '4d9eab13620fe3569ba3b0e56e2877739e4145e3', '0xec67005c4e498ec7f55e092bd1d35cbc47c91892', '0d821bd7b6d53f5c2b40e217c6defc8bbe896cf5', '0xa1d0E215a23d7030842FC67cE582a6aFa3CCaB83', '0x57Ab1ec28D129707052df4dF418D58a2D46d5f51', '0x9aab071b4129b083b01cb5a0cb513ce7eca26fa5', '0x83e6f1e41cdd28eaceb20cb649155049fac3d5aa', '0x115eC79F1de567eC68B7AE7eDA501b406626478e', '0xb59490ab09a0f526cc7305822ac65f2ab12f9723', '0x2ef52Ed7De8c5ce03a4eF0efbe9B7450F2D7Edc9', '0xe5b826ca2ca02f09c1725e9bd98d9a8874c30532', '0xba5BDe662c17e2aDFF1075610382B9B691296350', '0xd084b83c305dafd76ae3e1b4e1f1fe2ecccb3988', '0x249e38ea4102d0cf8264d3701f1a0e39c4f2dc3b', '0x765de816845861e75a25fca122bb6898b8b1282a', 'poLisWXnNRwC6oBu1vHiuKQzFjGL4XDSu4g9qjz9qVk', '0x4b9278b94a1112cAD404048903b8d343a810B07e', '0xf486ad071f3bee968384d2e39e2d8af0fcf6fd46', '0x814e0908b12a99fecf5bc101bb5d0b8b5cdf7d26', '0x993864e43caa7f7f12953ad6feb1d1ca635b875f', '0x865ec58b06bf6305b886793aa20a2da31d034e68', '0xCa3F508B8e4Dd382eE878A314789373D80A5190A', '0x53c8395465a84955c95159814461466053dedede', '0x80d55c03180349fff4a229102f62328220a96444', '0x61e90a50137e1f645c9ef4a0d3a4f01477738406', '0x15b7c0c907e4C6b9AdaAaabC300C08991D6CEA05', '0xa1d65e8fb6e87b60feccbc582f7f97804b725521', '0xf920e4f3fbef5b3ad0a25017514b769bdc4ac135', '0x226bb599a12c826476e3a771454697ea52e9e220', '0xb661f4576d5e0b622fee6ab041fd5451fe02ba4c', '0xdbdb4d16eda451d0503b854cf79d55697f90c8df', '0xcc4304a31d09258b0029ea7fe63d032f52e44efe', '0x37a56cdcD83Dce2868f721De58cB3830C44C6303', '0xb4b9dc1c77bdbb135ea907fd5a08094d98883a35', '0x2a3bff78b79a009976eea096a51a948a3dc00e34', '0xE02dF9e3e622DeBdD69fb838bB799E3F168902c5', '0x306ee01a6bA3b4a8e993fA2C1ADC7ea24462000c', '0xecc000ebd318bee2a052eb174a71faf2c3c9e898', '0xa9b1eb5908cfc3cdf91f9b8b3a74108598009096', '0xf203Ca1769ca8e9e8FE1DA9D147DB68B6c919817', '0xb705268213d593b8fd88d3fdeff93aff5cbdcfae', 'GASBLVHS5FOABSDNW5SPPH3QRJYXY5JHA2AOA2QHH2FJLZBRXSG4SWXT', '602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7', '0xf0d33beda4d734c72684b5f9abbebf715d0a7935', '0x1ceb5cb57c4d4e2b2433641b95dd330a33185a44', '0x33D0568941C0C64ff7e0FB4fbA0B11BD37deEd9f', '0x2A8e1E676Ec238d8A992307B495b45B3fEAa5e86', '0x46d0DAc0926fa16707042CAdC23F1EB4141fe86B', '0x2559813bbb508c4c79e9ccce4703bcb1f149edd7', '0xb9F747162AB1E95d07361f9048BcDF6eDdA9eEA7', '0x84ca8bc7997272c7cfb4d0cd3d55cd942b3c9419', '0x2a9bDCFF37aB68B95A53435ADFd8892e86084F93']

##add to list
list_transfer_signatures = ["0xa9059cbb", "0x8abdfa02" ]

transaction_count = {} # recipient_address: num_transactions

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
    recipient_address = "0x" + transaction_data[10:74].lstrip("0")

    if erc20_address in transaction_count:
        if recipient_address in transaction_count[erc20_address]:
            transaction_count[erc20_address][recipient_address] += 1
        else:
            transaction_count[erc20_address][recipient_address] = 1
    else:
        transaction_count[erc20_address] = {recipient_address : 1}

    # TODO: Check if exchnage wallet (isn't this the if check in the sybil attack func)
    #what alert id do we raise, severity, ect

    # TODO: make a set for addresses we've thrown an alert for already and don't throw a second alert if alerted before.

    if transaction_count[erc20_address][recipient_address] > 5 and transaction_count[erc20_address][recipient_address] < 500:
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
        print(transaction_count)

    # if(checkSybil(w3, transaction_event, recipient_address, erc20_address)):
    #     findings.append( Finding({
    #     'name': 'Sybil Attack',
    #     'description': f'{recipient_address} wallet may be involved in a Sybil Attack for token {erc20_address}',
    #     'alert_id': 'FORTA-7',
    #     'type': FindingType.Info,
    #     'severity': FindingSeverity.Info,
    #     'metadata': {
    #         "transaction_id": transaction_event.transaction.hash,
    #         'from': erc20_address,
    #         'to': recipient_address
    #     }}))
    #     logging.debug(f"Potential Sybil attck identified {findings}")
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

    # TODO: this probably needs to change. As it is right now, this looks at transfers IN THIS TRANSACTION only.
    token_transfer_events = transaction_event.filter_log(ERC_20_TRANSFER_EVENT_ABI, erc20_address)

    print(token_transfer_events)
    # find all erc20_address transactions going FROM the erc20_address to sender_address in the last week
    num_transactions = 0
    week_ago = datetime.now() - timedelta(weeks=1)

    '''
    Forta test case
    B->A
    C->A
    D->A
    E->A
    F->A


    B->T->B->T->A

    Airdrop -> B->T->A
               C->T->A
    D->T->A
    E->T->A
    F->T->A

    T->B ->A
    T->C ->A
    T->D ->A
    T->E ->A
    T->F ->A
    '''

    # timestamp >= week_ago
    for event in token_transfer_events:
        logging.debug(f"Token Transfer Event  {event}")
        timestamp = find_block_timestamp(w3, event.blockNumber)
        if event['args']['from'] == erc20_address and \
            event['args']['to'] == recipient_address:
            num_transactions += 1

    # [AttributeDict({'args': AttributeDict({'from': '0xf96cA963Fb2bE5c4eAF47C22c36cF2Fa26231e7f', 'to': '0xee9bd0E71681ee6E9Aa9F1ba46D2D1149f7BD054', 'value': 2000000000000000000000}), 'event': 'Transfer', 'logIndex': 26, 'transactionIndex': 9, 'transactionHash': '0x0afefa0d6262c4ef2bd22314647a8ad5b222bb8d3952780ca219849c826c0218', 'address': '0x41545f8b9472d758bb669ed8eaeeecd7a9c4ec29', 'blockHash': '0x580f931f76b7331e669958e0ddd5d43c283cb808792c868d638cee350223df60', 'blockNumber': 14971787})]

    # if more than 5 and less than 500, throw alert
    if num_transactions > 5 and num_transactions < 500:
        return True
    else:
        # 500 is probably larger than any sybil attack, in which case its an exchange wallet
        return False


def handle_transaction(transaction_event):
    # return real_handle_transaction(transaction_event)
    return analyze_transaction(w3, transaction_event)


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
