import logging
import time

from web3.exceptions import ABIFunctionNotFound

from package import units, const
from package.chain import Chain
from package.gas_estimator import get_gas_price

log = logging.getLogger(__name__)


def swap(src_token, dest_token, swap_amount, wallet_address, slippage=const.DEFAULT_SLIPPAGE, gas_speed=const.DEFAULT_SPEED,
         token_swap_expire_transaction=const.TOKEN_SWAP_EXPIRE_TRANSACTION):
    log.debug(f"[d] swap()")
    web3 = Chain().get_w3()
    buy = False

    private_key = Chain().get_private_key()
    spender_address = Chain().get_router_contract()
    swap_amount_rounded = get_rounded_amount(swap_amount, src_token.get_units())

    amount_out_min = int((1 - slippage/100) * get_amounts_out(src_token, token_dst=dest_token, amount=swap_amount)[-1])

    log.info(f"[d] Amounts_out_min: {get_rounded_amount(amount_out_min, dest_token.get_units())} slippage {slippage}")
    log.info(f"[d] Full amount_out_min: {amount_out_min}")
    log.info(f"[d] Get_amounts_out: {get_amounts_out(src_token, token_dst=dest_token, amount=swap_amount)}")

    if dest_token.get_checksum_address() == web3.toChecksumAddress(Chain().get_native_token()):
        if Chain().get_router_name() == const.ROUTER_TRADERJOE:
            swap_function = spender_address.functions.swapExactTokensForAVAX
            log.info("[d] Using swapExactTokensForAVAX")
        else:
            swap_function = spender_address.functions.swapExactTokensForETH
            log.info("[d] Using swapExactTokensForETH")
    elif src_token.get_checksum_address() == web3.toChecksumAddress(Chain().get_native_token()):
        buy = True
        if Chain().get_router_name() == const.ROUTER_TRADERJOE:
            swap_function = spender_address.functions.swapExactAVAXForTokens
            log.info("[d] Using swapExactAVAXForTokens")
        else:
            swap_function = spender_address.functions.swapExactETHForTokens
            log.info("[d] Using swapExactETHForTokens")
    else:
        swap_function = spender_address.functions.swapExactTokensForTokens
        log.info("[d] Using swapExactTokensForTokens")

    expire_date = int(time.time()) + token_swap_expire_transaction

    log.info(f"[d] Swap amount: {swap_amount_rounded} src_token {src_token.get_symbol()} dst_token {dest_token.get_symbol()}")
    log.info(f"[d] Wallet_address {wallet_address} expire date {time.ctime(expire_date)}")

    txn = None

    try:
        if buy:
            swap_ret = swap_function(amount_out_min,
                                     [src_token.get_checksum_address(), dest_token.get_checksum_address()],
                                     wallet_address, expire_date)
            txn = swap_ret.buildTransaction({
                'value': swap_amount,
                'from': wallet_address,
                'nonce': web3.eth.get_transaction_count(wallet_address)
            })
        else:
            swap_ret = swap_function(swap_amount, amount_out_min,
                                 [src_token.get_checksum_address(), dest_token.get_checksum_address()],
                                 wallet_address, expire_date)
            txn = swap_ret.buildTransaction({
                'from': wallet_address,
                'nonce': web3.eth.get_transaction_count(wallet_address)
            })

        gwei = get_gas_price(gas_speed)
        gas = 250000

        # Original version with increased gas:
        # txn['gas'] = int(web3.eth.estimate_gas(txn) * 1.2)
        # Alternative version: # TESTING: BSC, MATIC, AVAX
        txn['gas'] = gas
        txn['gasPrice'] = gwei
        # You can check the % in Gas Limit & Usage by Txn: to see if * 1.2 works

        log.info(f"[+] Original gas: {int(web3.eth.estimate_gas(txn))} increased gas: {txn['gas']} "
                 f"and gasPrice: {get_rounded_amount(txn['gasPrice'], 'gwei')} gwei")
        log.info(f"[+] Alternative version: gasPrice: {gwei} and gas limit: {gas}")
        # how much gas here? https://help.crypto.com/en/articles/5129582-what-is-nonce-gas-price-and-gas-limit
        # REVERIFY: 21000 transaction; 173482-556k uniswap 162k pcs; 256k-304k qs 51k app uni

    except ValueError as e:
        if "TRANSFER_FROM_FAILED" in e.args[0]:
            print("[?] TRANSFER_FROM_FAILED: Not enough tokens?")
            # TODO: aici ar trebui să afișez TXN deși îmi iese că de fapt merge swapul!!! dar nu e trimisă tranz.. wtf?
        elif "INSUFFICIENT_INPUT_AMOUNT" in e.args[0]:
            print("[?] INSUFFICIENT_INPUT_AMOUNT: Not enough tokens? Token not approved?")
        elif "INSUFFICIENT_OUTPUT_AMOUNT" in e.args[0]:
            print("[?] INSUFFICIENT_OUTPUT_AMOUNT: Multihop not supported or Slippage too low.")
        elif "INVALID_PATH" in e.args[0]:
            print("[?] INVALID_PATH: Multihop not supported or using private key.")
        elif "execution reverted" in e.args[0]:
            print(f"[?] ContractLogicError, maybe you should increase gas to 25000 on BSC? ({e.args[0]})") # TODO: add try again option?
            print(f"[?] Or you're using a PCS clone on Chapel? ({e.args[0]})")
        else:
            log.error("[?] Untreated exception!")
            print(e.args[0])
        log.error(e.args[0])
        raise e


    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_hash = None
    try:
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    except ValueError as e:
        if e.args[0].get('message') in 'intrinsic gas too low':
            result = ["Failed", f"ERROR: {e.args[0].get('message')}"]
            print(result)
        elif e.args[0].get('code') == -32000:
            print("[?] Replacement transaction underpriced. Either increase the gas "
                  f"or check for an unmined transaction.")
            # print("[+] Increasing gas.")
            # txn['gas'] = int(txn['gas'] * 1.101)
            # signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
            # tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            # # print(web3.eth.getTransaction(txn).gasPrice)
            # # replacement_price = web3.eth.getTransaction(pending_txn_hash).gasPrice * 1.101
        else:
            result = ["Failed", f"ERROR: {e.args[0].get('message')} : {e.args[0].get('code')}"]
            print(result)
        log.error(e.args[0])
        raise e
    return web3.toHex(tx_hash)


# @timeit
def wait_for_token(wallet_address, token_address, token_abi=const.token_abi,
                   token_wait_time=const.DEFAULT_TOKEN_WAIT_TIME,
                   display_decimals=const.DISPLAY_DECIMALS):
    log.debug(f"[d] wait()")
    web3 = Chain().get_w3()

    token_address = web3.toChecksumAddress(token_address)
    token_contract = web3.eth.contract(token_address, abi=token_abi)
    token_symbol = token_contract.functions.symbol().call()
    try:
        token_decimals = token_contract.functions.decimals().call()
    except ABIFunctionNotFound:
        token_decimals = 10 ** 18
    token_units = units.get_unit(token_decimals)

    token_initial_balance_full = token_contract.functions.balanceOf(wallet_address).call()
    token_initial_balance = web3.fromWei(token_initial_balance_full, token_units)

    print(f"[+] Current {token_symbol} balance: {round(token_initial_balance, display_decimals)} ")
    print(
        f"[+] Watching wallet {wallet_address} for token {token_symbol} ({token_address}) every {token_wait_time}s")

    new_balance_full = token_initial_balance_full
    while new_balance_full <= token_initial_balance_full:
        time.sleep(token_wait_time)
        try:
            new_balance_full = token_contract.functions.balanceOf(wallet_address).call()
        except ValueError as e:
            if "Bad gateway for url" in e.args[0]:
                print("[?] RPC error")
                raise(e)
                # TODO: reconnect with different RPC

    final_balance_full = new_balance_full - token_initial_balance_full
    final_balance = web3.fromWei(final_balance_full, token_units)

    print(f"[+] {round(final_balance, display_decimals)} {token_symbol} arrived in wallet. Total balance: "
          f"{round(web3.fromWei(new_balance_full, token_units), display_decimals)} ")
    time.sleep(1) # We need sleep in case of a swap following the wait because of INSUFFICIENT_INPUT_AMOUNT: or replacement transaction underpriced being thrown.
    return


# @timeit
def wait_for_transaction(tx_hash):
    log.debug(f"[d] wait_for_transaction()")
    web3 = Chain().get_w3()

    try:
        web3.eth.wait_for_transaction_receipt(tx_hash)
        # TODO: add timeout https://github.com/sjoerd1999/Avalanche-Python-API/blob/fd38a9b9b10149b4d19769be12ce37c50bf3b76b/AvalancheAPI.py#L100
    except ValueError as e:
        print("[?] Are we here?")
        # TODO: catch TimeExhausted Transaction... is not in the chain, after ... seconds
        if "TimeExhausted" in e.args[0]:
            url = Chain().get_url_tx(tx_hash)
            print("[?] TimeExhausted: Waited for transaction for too long. Check what happened: " + url)
            log.error(e.args[0])
            raise e
        else:
            log.error(e.args[0])
            result = ["[?] Failed", f"ERROR: {e.args[0].get('message')} : {e.args[0].get('code')}"]
            print(result)
            raise e
    except Exception as e:
        print(e.args[0])
        log.error(e.args[0])
        raise e

    return True


# @timeit
def approve(token, wallet, max_amount=const.APPROVAL_AMOUNT):
    log.debug(f"[d] approve()")
    web3 = Chain().get_w3()
    token_contract = token.get_contract()
    wallet_address = wallet.get_address()
    private_key = Chain().get_private_key()
    spender = Chain().get_router_address()

    nonce = web3.eth.getTransactionCount(wallet_address)

    log.info(f"[+] Spender: {spender} max_amount: {max_amount} wallet: {wallet}")
    tx = token_contract.functions.approve(spender, max_amount).buildTransaction({
        'from': wallet_address,
        'nonce': nonce
        #    'gasPrice': web3.toWei('...', 'gwei'), # do we need to speed up approvals?
    })

    signed_tx = web3.eth.account.signTransaction(tx, private_key)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

    log.info(f"[+] Approving token {token.get_symbol()} in transaction: {Chain().get_url_tx(web3.toHex(tx_hash))}")
    wait_for_transaction(tx_hash)
    return web3.toHex(tx_hash)

def is_approved(token, wallet, approval_amount=const.APPROVAL_AMOUNT):
    allowance = token.get_contract().functions.allowance(wallet.get_checksum_address(), Chain().get_router_address()).call()
    log.info(f"[+] {allowance} < {approval_amount} = {allowance < approval_amount}")
    if allowance < approval_amount:
        return False
    else:
        return True


def connect(network, router=None, private_key=None, timeout=const.WEB3_TIMEOUT):
    web3 = Chain(network=network, router=router, private_key=private_key, timeout=timeout).get_w3()
    if Chain().is_connected():
        msg = f"[+] Connected to {Chain().get_name()}"
        log.info(msg)
        print(msg)
    else:
        msg = f"[?] Not connected to {Chain().get_name()}"
        log.info(msg)
        raise Exception(msg)
    return web3


def show_balance(token, token_dst, wallet):
    print(f"[+] Wallet balance:")
    print(f"\t{wallet.get_symbol()}: {wallet.get_rounded_balance()}"
          f"\t{token.get_symbol()}: {token.get_rounded_balance(wallet.get_address())}"
          f"\t{token_dst.get_symbol()}: {token_dst.get_rounded_balance(wallet.get_address())}")


def get_amounts_out(token, token_dst=None, wallet=None, amount=None):
    web3 = Chain().get_w3()
    router = Chain().get_router_contract()

    log.info(f'[+] {token.get_symbol()} -> {token_dst.get_symbol() if token_dst else None} amount: {get_rounded_amount(amount, token.get_units()) if amount else None} wallet: {wallet}')

    if Chain().get_router_name() == const.ROUTER_TRADERJOE:
        get_network_address = router.functions.WAVAX()
        log.info("[d] using Chain().get_router_contract().functions.WAVAX")
    else:
        get_network_address = router.functions.WETH()
        log.info("[d] using Chain().get_router_contract().functions.WETH")

    if (token.get_checksum_address() == get_network_address.call() and not token_dst) or \
            (token.get_checksum_address() == get_network_address.call() and token_dst.get_checksum_address() == get_network_address.call()):
        amount = web3.toWei(1, token.get_units())
        return amount, amount
    elif token_dst and token_dst.get_checksum_address() != get_network_address.call() and token.get_checksum_address() != get_network_address.call():
        sell_token_contract_address = token.get_checksum_address()
        buy_token_contract_address = token_dst.get_checksum_address()
        path = [sell_token_contract_address, get_network_address.call(), buy_token_contract_address]
    elif token_dst and (token_dst.get_checksum_address() == get_network_address.call() or token.get_checksum_address() == get_network_address.call()):
        sell_token_contract_address = token.get_checksum_address()
        buy_token_contract_address = token_dst.get_checksum_address()
        path = [sell_token_contract_address, buy_token_contract_address]
    else:
        sell_token_contract_address = token.get_checksum_address()
        buy_token_contract_address = get_network_address.call()
        path = [sell_token_contract_address, buy_token_contract_address]

    if wallet:
        try:
            amount = token.get_contract().functions.balanceOf(wallet.get_address()).call()
        except ValueError as e:
            if "Web3.py only accepts checksum addresses" in e.args[0]:
                log.error(e)
                log.error("[?] Maybe you've used a wallet address instead of a token address?")
                exit(1)
            raise e
    elif amount is None:
        amount = web3.toWei(1, token.get_units())
    # else:
    #     starting_amount = web3.toWei(starting_amount, token.get_units()) # swap already sends as wei
    #     print(starting_amount)

    try:
        amounts = router.functions.getAmountsOut(amount,
                                                 path
                                                 ).call()
    except ValueError as e:
        if "IDENTICAL_ADDRESSES" in e.args[0]:
            log.error("[?] Token address should be the token we plan on trading, not the network token.")
            exit(1)
        if "INSUFFICIENT_INPUT_AMOUNT" in e.args[0]:
            return 0, 0
        if "execution reverted" in e.args[0]:
            log.error(f"[?] Unknown error: {e}. Maybe there's no liquidity?")
            # TODO: this happened when there were a lot of sells and a big number as amount... check if it happens again
            raise(e)
        raise e
    return amounts # 2 or more amounts depending on path


def get_rounded_amount(amount, units=None, decimals=const.DISPLAY_DECIMALS):
    web3 = Chain().get_w3()
    if units:
        amount = web3.fromWei(amount, units)
    return round(amount, decimals)
