#!/usr/bin/env python3


import logging
import os
import sys

import config
from package import cmd_args_pecunia, const
from package.announcer import Announcer
from package.chain import Chain
from package.token import Token, Wallet
from package.utils import get_private_key
from package.web3_functions import approve, swap, wait_for_token, wait_for_transaction, connect, show_balance, \
    is_approved

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def main(cfg, announcer):
    private_key = None
    if cfg["token_swap"] or cfg["token_approve"]:
        private_key = get_private_key()
        if cfg["token_wait_time"] > const.WEB3_TIMEOUT:
            timeout = cfg["token_wait_time"] * 1.2
        else:
            timeout = const.WEB3_TIMEOUT
        try:
            web3 = connect(network=cfg["network"], router=cfg["router"], private_key=private_key, timeout=timeout)
        except Exception as e:
            log.error(e)
            announcer.print_and_voice(e)
            exit(1)
    else:
        if cfg["token_wait_time"] > const.WEB3_TIMEOUT:
            timeout = cfg["token_wait_time"] * 1.2
        else:
            timeout = const.WEB3_TIMEOUT
        try:
            web3 = connect(network=cfg["network"], timeout=timeout)
        except Exception as e:
            log.error(e)
            announcer.print_and_voice(e)
            exit(1)

    wallet = Wallet(cfg["wallet_address"])
    try:
        token = Token(cfg["token_address"])
    except Exception as e:
        exit(1)


    if (cfg["token_swap"] or cfg["token_approve"]):
        if not is_approved(token, wallet):
            log.info(f"[+] Approving {token.get_symbol()} for trading.")
            approve(token, wallet)
            announcer.print_and_voice(f"[+] Token {token.get_symbol()} approved.")
        else:
            print(f"[+] Token {token.get_symbol()} already approved.")
            log.info(f"[+] Token {token.get_symbol()} already approved.")

    if cfg["token_wait"]:
        log.info("[+] wait_for_token")
        try:
            wait_for_token(wallet.get_address(), token.get_address(), token_wait_time=cfg["token_wait_time"])
        except Exception as e:
            log.error(e)
            log.error(f'wait_for_token() exited prematurely!')
            announcer.all(f'wait_for_token() exited prematurely!')
            exit(1)

        if not cfg["token_swap"]:
            announcer.all(f'[+] Token {token.get_symbol()} received.')
        else:
            announcer.voice("Token received")

    if cfg["token_swap"]:
        log.info("[+] token_swap")
        try:
            token_dst = Token(cfg["token_dst_address"])
        except Exception as e:
            exit(1)

        show_balance(token, token_dst, wallet)

        if cfg["token_swap_all"]:
            swap_amount = token.find_balance_full(wallet.get_address())
        else:
            swap_amount = web3.toWei(cfg["token_swap_amount"], token.get_units())

        print(
            f'[+] Swapping: {web3.fromWei(swap_amount, token.get_units())} {token.get_symbol()} for '
            f'{token_dst.get_symbol()} with {cfg["gas_speed"]} speed and slippage {cfg["slippage"]}')

        try:
            tx_hash = swap(token, token_dst, swap_amount, wallet_address=wallet.get_address(), slippage = cfg["slippage"],
                           gas_speed=cfg["gas_speed"])
        except Exception as e:
            log.error(e)
            log.error("[?] swap() exited prematurely! Slippage issues?")
            announcer.all(f'[?] swap() exited prematurely! Slippage issues?')
            exit(1)

        print(f'[+] Swap transaction for {token.get_symbol()}: {Chain().get_url_tx(tx_hash)}')
        wait_for_transaction(tx_hash)
        announcer.all(f'[+] Token {token.get_symbol()} sold')

        show_balance(token, token_dst, wallet)


if __name__ == "__main__":
    if len(sys.argv) != 1:
        cfg = cmd_args_pecunia.get_arguments(sys.argv)
    else:
        cfg = {"network": config.network,
               "router": config.router_name, "wallet_address": config.wallet_address,
               "token_address": config.token_address, "token_swap": config.token_swap,
               "token_swap_all": config.token_swap_all, "token_dst_address": config.token_dst_address,
               "token_swap_amount": config.token_swap_amount, "token_wait": config.token_wait,
               "use_pushsafer": config.use_pushsafer, "use_mac_voice": config.use_mac_voice,
               "gas_speed": config.GAS_SPEED, "slippage": config.SLIPPAGE, "token_wait_time": config.TOKEN_WAIT_TIME,
               "token_approve": const.APPROVE}

    announcer = Announcer(use_pushsafer=cfg["use_pushsafer"], pushsafer_key=config.pushsafer_key,
                          use_voice=cfg["use_mac_voice"])

    try:
        main(cfg, announcer)
    except KeyboardInterrupt:
        print('\n[!] Interrupted')
        try:
            exit(0)
        except SystemExit:
            exit(0)
    except Exception as e:
        print("[+] Exception. Treat it before this moment.")
        announcer.all("Exception encountered!")
        raise e
