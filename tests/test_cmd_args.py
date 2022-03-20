import os
from unittest import TestCase

from package.cmd_args_pecunia import *


class TestCmdArgs(TestCase):

    def test_get_arguments_for_approve(self):
        network = "eth"
        router = "uniswap"
        wallet = "0x000000000000000000000000000000000000000"
        token = "0x000000000000000000000000000000000000000"

        args = f'./pecunia_ad_vitam.py -n {network} -r {router} ' \
               f'-w {wallet} -t {token} ' \
               '--approve'
        args = args.split(sep=' ')

        config_dict = get_arguments(args)
        self.assertEqual(network, config_dict["network"])
        self.assertEqual(router, config_dict["router"])
        self.assertEqual(wallet, config_dict["wallet_address"])
        self.assertEqual(token, config_dict["token_address"])
        self.assertTrue(config_dict["token_approve"])

    def test_get_arguments_sell_quickly_amount(self):
        network = "ropsten"
        router = "uniswap"
        wallet = "0x000000000000000000000000000000000000000"
        token = "0x000000000000000000000000000000000000000"
        token_dst = "0x000000000000000000000000000000000000000"
        amount = 10
        speed = "urgent"

        args = f'./pecunia_ad_vitam.py -n {network} -r {router} ' \
               f'-w {wallet} -t {token} -d {token_dst} -a {amount} --speed {speed}'
        args = args.split(sep=' ')

        config_dict = get_arguments(args)
        self.assertEqual(network, config_dict["network"])
        self.assertEqual(router, config_dict["router"])
        self.assertEqual(wallet, config_dict["wallet_address"])
        self.assertEqual(token, config_dict["token_address"])
        self.assertEqual(token_dst, config_dict["token_dst_address"])
        self.assertEqual(amount, config_dict["token_swap_amount"])
        self.assertEqual(speed, config_dict["gas_speed"])

    def test_get_arguments_for_dump(self):
        network = "bsc"
        router = "pancakeswap"
        wallet = "0x000000000000000000000000000000000000000"
        token = "0x000000000000000000000000000000000000000"
        token_dst = "0x000000000000000000000000000000000000000"
        speed = "fast"

        args = f'./pecunia_ad_vitam.py -n {network} -r {router} ' \
               f'-w {wallet} -t {token} -d {token_dst} --dump --speed {speed}'
        args = args.split(sep=' ')
        config_dict = get_arguments(args)
        self.assertEqual(network, config_dict["network"])
        self.assertEqual(router, config_dict["router"])
        self.assertEqual(wallet, config_dict["wallet_address"])
        self.assertEqual(token, config_dict["token_address"])
        self.assertEqual(token_dst, config_dict["token_dst_address"])
        self.assertEqual(speed, config_dict["gas_speed"])
        self.assertTrue(config_dict["token_swap_all"])

    def test_not_enough_arguments(self):
        args = f'./pecunia_ad_vitam.py 2 3 4 5 6 7 8 9'
        args = args.split(sep=' ')
        self.assertRaises(SystemExit, get_arguments, args)

    def test_wrong_arguments(self):
        router = "quickswap"
        wallet = "0x000000000000000000000000000000000000000"
        token = "0x000000000000000000000000000000000000000"

        args_missing_value = f'./pecunia_ad_vitam.py -n -r {router} ' \
                             f'-w {wallet} -t {token} ' \
                             '--approve'
        args = args_missing_value.split(sep=' ')
        self.assertRaises(SystemExit, get_arguments, args)

        args_missing_argument = f'./pecunia_ad_vitam.py 3 -r {router} ' \
                                f'-w {wallet} -t {token} ' \
                                '--approve'
        args = args_missing_argument.split(sep=' ')
        self.assertRaises(SystemExit, get_arguments, args)
