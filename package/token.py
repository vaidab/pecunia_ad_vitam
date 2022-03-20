import logging

from web3.exceptions import BadFunctionCallOutput

from package import units, const
from package.chain import Chain

log = logging.getLogger(__name__)


# For our purpose we can link our wallet address to each token
class Token:
    def __init__(self, address):
        self.address = address
        try:
            self.checksum_address = Chain().get_w3().toChecksumAddress(self.address)
        except ValueError as e:
            if "Unknown format " in e.args[0]:
                msg = f'[?] Unknown token address format: "{self.address}"'
                print(msg)
                log.error(msg)
            else:
                msg = f'[?] {e}'
                print(msg)
                log.error(msg)
            raise(e)
        except TypeError as e:
            if "Exactly one of the passed values can be specified" in e.args[0]:
                msg = f'[?] Missing token address: "{self.address}"'
                print(msg)
                log.error(msg)
            else:
                msg = f'[?] {e}'
                log.error(msg)
            raise(e)

        self.contract = Chain().get_w3().eth.contract(self.checksum_address, abi=const.token_abi)
        try:
            self.symbol = self.contract.caller.symbol()  # exits if bad contract
        except BadFunctionCallOutput as e:
            msg = f"[?] Invalid contract (maybe a wallet) or wrong network? Error: {e}"
            print(msg)
            log.error(msg)
            raise(e)
        self.decimals = self.contract.caller.decimals()
        if self.decimals == 8: # TODO: 0xB0eB3e295B44d7D405ba8026A9734A9ab354a8B2 != 8 decimals
            msg = f"[?] Unsupported decimals: {self.decimals} for {self.symbol}"
            print(msg)
            log.error(msg)
            raise TypeError(msg)
        self.units = units.get_unit(self.decimals)

    def get_address(self):
        return self.address

    def get_checksum_address(self):
        return self.checksum_address

    def get_units(self):
        return self.units

    def get_symbol(self):
        return self.symbol

    def find_balance_full(self, wallet):
        return self.contract.functions.balanceOf(wallet).call()

    def find_balance(self, wallet):
        return Chain().get_w3().fromWei(self.find_balance_full(wallet), self.units)

    def get_rounded_balance(self, wallet, max_decimals=const.DISPLAY_DECIMALS):
        return round(self.find_balance(wallet), max_decimals)

    def get_contract(self):
        return self.contract


class Wallet(Token):
    def __init__(self, address):
        self.address = address
        try:
            self.checksum_address = Chain().get_w3().toChecksumAddress(self.address)
        except ValueError as e:
            if "Unknown format " in e.args[0]:
                log.error(f'[?] Unknown token address format: "{self.address}"')
                exit(1)
        except TypeError as e:
            if "Exactly one of the passed values can be specified" in e.args[0]:
                log.error(f'[?] Missing token address: "{self.address}"')
            exit(1)

        self.symbol = Chain().get_native_currency_symbol()
        self.decimals = Chain().get_native_currency_decimals()
        self.units = units.get_unit(self.decimals)

    def find_balance_full(self):
        return Chain().get_w3().eth.getBalance(self.checksum_address)

    def find_balance(self):
        return Chain().get_w3().fromWei(self.find_balance_full(), self.units)

    def get_rounded_balance(self, max_decimals=const.DISPLAY_DECIMALS):
        return round(self.find_balance(), max_decimals)


def main():
    print(Token("0xc778417e063141139fce010982780140aa0cd5ab"))


if __name__ == "__main__":
    main()
