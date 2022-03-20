import getopt
import logging

from package import const, utils, encryption

log = logging.getLogger(__name__)

options = "n:r:w:t:d:a:vph"
long_options = ["network=", "router=", "wallet=", "token=",
                "dest=", "amount=", "dump", "speed=", "wait=", "approve", "swap",
                "slippage=", "voice", "pushsafer", "password", "help", "encrypt"]


def get_arguments(args):
    argument_list = args[1:]
    cfg = {
        'network': None,
        'router': None,
        'wallet_address': None,
        'token_address': None,
        'token_dst_address': None,
        'token_swap': False,
        'token_swap_amount': 0,
        'token_swap_all': False,
        'gas_speed': const.DEFAULT_SPEED,
        'token_wait': False,
        'token_wait_time': const.DEFAULT_TOKEN_WAIT_TIME,
        'token_approve': False,
        'slippage': const.DEFAULT_SLIPPAGE,
        'use_pushsafer': False,
        'use_mac_voice': False,
        'use_private_password': False
    }

    try:
        arguments, values = getopt.getopt(argument_list, options, long_options)
        if len(args) < 8 and len(args) != 2:
            show_usage()
            exit(1)

        for currentArgument, currentValue in arguments:
            if currentArgument == "--encrypt":
                encryption.encrypt_private_key()
                exit(1)
            elif currentArgument in ("-n", "--network"):
                cfg['network'] = currentValue
            elif currentArgument in ("-r", "--router"):
                cfg['router'] = currentValue
            elif currentArgument in ("-w", "--wallet"):
                cfg['wallet_address'] = currentValue
            elif currentArgument in ("-t", "--token"):
                cfg['token_address'] = currentValue
            elif currentArgument in ("-d", "--dest"):
                cfg['token_dst_address'] = currentValue
            elif currentArgument == "--swap":
                cfg['token_swap'] = True
            elif currentArgument in ("-a", "--amount"):
                cfg['token_swap_amount'] = float(currentValue)
            elif currentArgument == "--dump":
                cfg['token_swap_all'] = True
            elif currentArgument == "--speed":
                cfg['gas_speed'] = currentValue
            elif currentArgument == "--wait":
                cfg['token_wait'] = True
                cfg['token_wait_time'] = int(currentValue)
            elif currentArgument == "--approve":
                cfg['token_approve'] = True
            elif currentArgument == "--slippage":
                cfg['slippage'] = int(currentValue)
            elif currentArgument in ("-v", "--voice"):
                cfg['use_mac_voice'] = True
            elif currentArgument == "--pushsafer":
                cfg['use_pushsafer'] = True
            elif currentArgument in ("-p", "--password"):
                cfg['use_private_password'] = True
            elif currentArgument in ("-h", "--help"):
                show_usage()
                exit(1)
            else:
                print(f"Invalid argument: {currentArgument} with value: {currentValue}")
                exit(1)

    except Exception as err:
        print(str(err))
        show_usage()
        exit(1)

    basic_conditions = (
            bool(cfg['network']) and
            bool(cfg['wallet_address']) and
            bool(cfg['token_address'])
    )
    swapping_condition = not cfg['token_swap'] or (
            bool(cfg['token_swap']) ==
            (
                    bool(cfg['token_dst_address']) and
                    (
                            bool(cfg['token_swap_amount']) or
                            bool(cfg['token_swap_all'])
                    )
            )
    )

    log.info(f"Basic conditions: {basic_conditions} "
              f"Swapping condition: {swapping_condition}")

    if not basic_conditions or not swapping_condition:
        show_usage()
        exit(1)

    return cfg


def show_usage():
    print()
    print(
        "pecunia_ad_vitam.py -n network [-r router] -w wallet -t token -d token-dest "
        "--swap -a amount --dump --speed speed --approve --wait seconds --slippage amount -v --pushsafer -p -h")
    print("pecunia_ad_vitam.py --encrypt\n")
    print("If there are no arguments it will take the values from config.py\n")
    print("Usage:")
    print("\t-n network is one of these: eth/ropsten/bsc/chapel/polygon/avax/ftm")
    print("\t-r uniswap/pancakeswap/quickswap/traderjoe/apeswap/spiritswap/spookyswap * uniswap v3, pancakeswap & apeswap v2")
    print("\t-a amount is the number of tokens to swap (float)")
    print("\t--swap will activate swapping which required a destination token and an amount or the dump option")
    print("\t--dump dumps the token")
    print("\t--speed standard/fast/urgent for the gas speed")
    print("\t--approve will approve the token transaction")
    print("\t--wait seconds will wait for token to appear in wallet and check every X seconds")
    print("\t--slippage 1-100")
    print("\t-v will use system's voice to announce the transaction")
    print("\t--pushsafer will use Pushsafer to announce the transaction")
    print("\t-p will initiate a password input")
    print("\n\t--encrypt will encrypt a private key and display it to add to the config file")
    return


def show_arguments(config_dict):
    print(f'[+] Network file: "{config_dict["network"]}" and router "{config_dict["router"]}"')
    print(f'[+] Using wallet address "{config_dict["wallet_address"]}"')
    print(f'[+] Token address is "{config_dict["token_address"]}" and token destination address is: '
          f'"{config_dict["token_dst_address"]}"')
    print(f'[+] Swapping: "{config_dict["token_swap"]}" Amount: "{config_dict["token_swap_amount"]}" '
          f'Dump all: "{config_dict["token_swap_all"]}" Speed: "{config_dict["gas_speed"]}"')
    print(f'[+] Waiting for transaction: "{config_dict["token_wait"]}" every '
          f'"{config_dict["token_wait_time"]}" seconds')
    print(f'[+] Approving: "{config_dict["token_approve"]}"')
    print(f'[+] Pushsafer: "{config_dict["use_pushsafer"]}" Mac voice: "{config_dict["use_mac_voice"]}" '
          f'Private password: "{config_dict["use_private_password"]}"')
    return
