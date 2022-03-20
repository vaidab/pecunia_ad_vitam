from package import tokens, const

TOKEN_WAIT_TIME = 1  # check only once per 120 seconds until we're closer to IDO
GAS_SPEED = const.SPEED_FAST
SLIPPAGE = 5  # 5% slippage

use_mac_voice = True
use_pushsafer = False
pushsafer_key = ""
private_key = ""
INFURA_API_KEY = ""  # for ETH and ROPSTEN networks

token_wait = True
token_swap = True
token_swap_all = True
token_swap_amount = 10  # if token_swap_all is false we sell this amount

wallet_address = ""
network = const.CHAIN_BSC
router = const.ROUTER_PANCAKESWAP
token_address = tokens.bsc_token_usdc
token_dst_address = tokens.bsc_token_busd
