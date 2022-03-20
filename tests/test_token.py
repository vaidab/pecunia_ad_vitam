from unittest import TestCase

from package import const, tokens
from package.chain import Chain
from package.token import Token, Wallet


class TestToken(TestCase):
    def setUp(self):
        Chain(const.CHAIN_ROPSTEN)
        self.random_wallet = "0x5709fab0715f1bcbd6ac007d2c574982bacfb71d"
        self.wallet = Wallet(self.random_wallet)
        self.token_usdc = Token(tokens.ropsten_token_usdc)

    def test_get_address(self):
        self.assertEqual(self.wallet.get_address(), self.random_wallet)

    def test_get_checksum_address(self):
        self.assertEqual(self.token_usdc.get_checksum_address(),
                         Chain().get_w3().toChecksumAddress(tokens.ropsten_token_usdc))

    # def test_get_units(self):
    #     return
    #
    # def test_get_symbol(self):
    #     return
    #
    # def test_find_balance_full(self):
    #     return
    #
    # def test_find_balance(self):
    #     return
    #
    # def test_get_rounded_balance(self):
    #     return
    #
    # def test_get_contract(self):
    #     return
