import getopt
import logging

from package import const

log = logging.getLogger(__name__)

options = "n:r:w:t:d:a:h"
long_options = ["network=", "router=", "wallet=", "token=",
                "dest=", "amount=", "help"]


def get_arguments(args):
    argument_list = args[1:]
    cfg = {
        'network': None,
        'router': None,
        'wallet_address': None,
        'token_address': None,
        'token_dst_address': None,
        'token_amount': 0,
    }

    try:
        arguments, values = getopt.getopt(argument_list, options, long_options)
        if len(args) < 7:
            show_usage()
            exit(1)

        for currentArgument, currentValue in arguments:
            if currentArgument in ("-n", "--network"):
                cfg['network'] = currentValue
            elif currentArgument in ("-r", "--router"):
                cfg['router'] = currentValue
            elif currentArgument in ("-t", "--token"):
                cfg['token_address'] = currentValue
            elif currentArgument in ("-d", "--dest"):
                cfg['token_dst_address'] = currentValue
            elif currentArgument in ("-w", "--wallet"):
                cfg['wallet_address'] = currentValue
            elif currentArgument in ("-a", "--amount"):
                cfg['token_amount'] = int(currentValue)
            elif currentArgument in ("-h", "--help"):
                show_usage()
                exit(1)
            else:
                print(f"Invalid argument: {currentArgument} with value: {currentValue}")
                exit(1)

    except getopt.error as err:
        print(str(err))
        show_usage()
        exit(1)

    basic_conditions = cfg['network'] and cfg['router'] and cfg['token_address']

    log.info(f"Basic conditions: {basic_conditions} ")

    if not basic_conditions:
        show_usage()
        exit(1)

    return cfg


def show_usage():
    print()
    print(
        "get_price -n network -r router -t token [-d token-dest / -w wallet / -a amount] -h\n")
    print("Usage:")
    print("\t-n network is one of these: eth/ropsten/bsc/chapel/polygon/avax")
    print("\t-r uniswap/pancakeswap/quickswap/traderjoe/apeswap * uniswap v3, pancakeswap & apeswap v2")
    print("\t-t token to find the price of")
    print("\t-d token to convert the first token into")
    print("\t-w wallet to show the conversion of all the tokens in balance")
    print("\t-a amount is the number of tokens to convert")
    print("\t\nOptional conditions are exclusive excluding -t token -d token-dest -a amount")
    return


def show_arguments(config_dict):
    print(f'[+] Network file: "{config_dict["network"]}" and router "{config_dict["router"]}"')
    print(f'[+] Token address is "{config_dict["token_address"]}" and '
          f'token destination address is: "{config_dict["token_dst_address"]}"')
    print(f'[+] Using wallet address "{config_dict["wallet_address"]}"')
    print(f'[+] Amount: "{config_dict["token_amount"]}"')
    return
