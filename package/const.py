import logging
import os

from package import abis as abis

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

CHAIN_ETH = "eth"
CHAIN_ROPSTEN = "ropsten"
CHAIN_BSC = "bsc"
CHAIN_CHAPEL = "chapel"
CHAIN_POLYGON = "polygon"
CHAIN_AVAX = "avax"
CHAIN_FTM = "ftm"

UNITS = os.path.join(ROOT_DIR, "data/units.json")
# https://github.com/ethereum-lists/chains/tree/master/_data/chains
chain_list = {
    CHAIN_ETH: os.path.join(ROOT_DIR, "data/eip155-1.json"),
    CHAIN_ROPSTEN: os.path.join(ROOT_DIR, "data/eip155-3.json"),
    CHAIN_BSC: os.path.join(ROOT_DIR, "data/eip155-56.json"),
    CHAIN_CHAPEL: os.path.join(ROOT_DIR, "data/eip155-97.json"),
    CHAIN_POLYGON: os.path.join(ROOT_DIR, "data/eip155-137.json"),
    CHAIN_AVAX: os.path.join(ROOT_DIR, "data/eip155-43114.json"),
    CHAIN_FTM: os.path.join(ROOT_DIR, "data/eip155-250.json")
} # uses shortname from eip*.json


ROUTER_UNISWAP = "uniswap"
ROUTER_PANCAKESWAP = "pancakeswap"
ROUTER_QUICKSWAP = "quickswap"
ROUTER_TRADERJOE = "traderjoe"
ROUTER_APESWAP = "apeswap"
ROUTER_SPIRITSWAP = "spiritswap"
ROUTER_SPOOKYSWAP = "spookyswap"

APPROVE = True
APPROVAL_AMOUNT = 79228162514264337593543950335 # infinite
DISPLAY_DECIMALS = 2  # 2 is more visually appealing than 16
TOKEN_SWAP_EXPIRE_TRANSACTION = 200  # seconds until the transaction will expire
WEB3_TIMEOUT = 60

SPEED_STANDARD = "standard"
SPEED_FAST = "fast"
SPEED_URGENT = "urgent"

DEFAULT_SPEED = SPEED_FAST
DEFAULT_TOKEN_WAIT_TIME = 1
DEFAULT_SLIPPAGE = 5

token_abi = abis.token_abi

logging.basicConfig(filename="logs/logs.txt",
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)