import json
import logging
import re

from web3 import Web3

import config
from package import const, units
from package.classes import Singleton

log = logging.getLogger(__name__)


class Chain(metaclass=Singleton):
    def __init__(self, network=None, router=None, private_key=None, timeout=60):
        try:
            f = open(const.chain_list[network])
        except KeyError as e:
            print(f"[?] Invalid network: {network}")
            exit(0)
        self.data = json.load(f)
        f.close()
        self.w3 = Web3(Web3.HTTPProvider(self.get_rpc(), request_kwargs={'timeout': timeout}))
        self.private_key = None
        if private_key is not None:
            self.set_private_key(private_key)
        self.set_router(router)

    def set_router(self, router_name=None):
        if not router_name:
            router_name = self.data['routers'][0]['name']

        for i in range(len(self.data['routers'])):
            if self.data['routers'][i]['name'] == router_name:
                self.router_name =  self.data['routers'][i]['name']
                self.router_address = self.data['routers'][i]['address']
                self.router_abi = self.data['routers'][i]['abi']
                self.router_contract = self.w3.eth.contract(address=self.router_address, abi=self.router_abi)
                return

        msg = f"[?] Couldn't set router {router_name}"
        print(msg)
        log.error(msg)
        exit(1)

    def get_router_name(self):
        return self.router_name

    def get_router_address(self):
        return self.router_address

    def get_router_contract(self):
        return self.router_contract

    def get_router_abi(self):
        return self.router_abi

    def get_w3(self):
        return self.w3

    def set_private_key(self, private_key):
        regexp = re.compile("(0x)?[0-9a-f]{64}", re.IGNORECASE | re.ASCII)

        if (len(private_key) == 64 or len(private_key) == 66) and isinstance(private_key, str):
            if regexp.fullmatch(private_key) is not None:
                self.private_key = private_key
                return True
        raise ValueError("[?] Invalid private key format")

    def get_private_key(self):
        if self.private_key:
            return self.private_key
        raise ValueError("[?] Did you forget to set a private key?")

    def is_connected(self):
        if self.w3:
            return True
        else:
            return False

    def show_network_info(self):
        print(f"[+] Connected to: {self.data['name']}")
        print(f"[+] Symbol: {self.data['nativeCurrency']['symbol']}")
        print(f"[+] ChainId: {self.data['chainId']}")
        print(f"[+] RPC: {self.data['rpc'][0]}")
        return

    def get_rpc(self):
        rpc = self.data['rpc'][0]
        if rpc.find("${INFURA_API_KEY}"):
            rpc = rpc.replace("${INFURA_API_KEY}", config.INFURA_API_KEY)
        return rpc

    def get_name(self):
        return self.data['name']

    def get_shortname(self):
        return self.data['shortName']

    def get_explorer_url(self):
        return self.data['explorers'][0]['url']

    def get_native_currency_symbol(self):
        return self.data['nativeCurrency']['symbol']

    def get_native_currency_decimals(self):
        return int(self.data['nativeCurrency']['decimals'])

    def get_native_currency_units(self):
        return units.get_unit(self.get_native_currency_decimals())

    def get_native_token(self):
        return self.data['nativeCurrency']['address']

    def get_url_tx(self, transaction):
        return f"{self.get_explorer_url()}/tx/{transaction}"

    def get_url_address(self, address):
        return f"{self.get_explorer_url()}/address/{address}"


def main():
    chain = Chain(const.ROPSTEN)
    transaction = "0xb8ac77a4e4464b9fbeb3d380dc6ab318553479b982a033974a9d29ef7c718c35"
    print(chain.get_url_tx(transaction))
    wallet = "0xA363c3Cb4f8d30741477bEA1f32A52e9Ed3D2075"
    print(chain.get_url_address(wallet))

    chain.set_router("uniswap")
    print(chain.get_router_address())


if __name__ == "__main__":
    main()
