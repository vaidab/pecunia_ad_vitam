#!/usr/bin/env python3

import textwrap

import requests
from lxml import html
from web3 import middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy, fast_gas_price_strategy, slow_gas_price_strategy

from package import const
from package.chain import Chain
from package.const import SPEED_STANDARD, SPEED_FAST, SPEED_URGENT


def get_gas_price(gas_speed):
    shortname = Chain().get_shortname()
    if shortname == "bnb":
        return get_gas_price_bsc(gas_speed)
    if shortname == "MATIC":
        return get_gas_price_matic_site(gas_speed)
    if shortname == "eth":
        return get_gas_price_eth(gas_speed)
    if shortname == "bnbt":
        return get_gas_price_ropsten(gas_speed)
    if shortname == "Avalanche":
        return get_gas_price_avax(gas_speed)
    if shortname == "FTM":
        return get_gas_price_ftm(gas_speed)
    else:
        raise Exception(f"[?] Unknown network: {shortname}")


def get_gas_price_ropsten(speed):
    ropsten_speed_med = 1
    ropsten_speed_fast = 2
    ropsten_speed_urgent = 3

    if speed == SPEED_STANDARD:
        return ropsten_speed_med
    elif speed == SPEED_FAST:
        return ropsten_speed_fast
    elif speed == SPEED_URGENT:
        return ropsten_speed_urgent
    else:
        raise Exception(f"[?] Couldn't get speed {speed} for ROPSTEN")


def get_gas_price_bsc(speed):
    bsc_speed_med = 5
    bsc_speed_fast = 8
    bsc_speed_urgent = 13

    if speed == SPEED_STANDARD:
        return bsc_speed_med
    elif speed == SPEED_FAST:
        return bsc_speed_fast
    elif speed == SPEED_URGENT:
        return bsc_speed_urgent
    else:
        raise Exception(f"[?] Couldn't get speed {speed} for BSC")


def get_gas_price_bsc_site(speed):
    speed_string = None
    if speed == SPEED_STANDARD:
        speed_string = "standardgas"
    elif speed == SPEED_FAST:
        speed_string = "fastgas"
    elif speed == SPEED_URGENT:
        speed_string = "rapidgas"

    url = "https://bscscan.com/gastracker"
    return get_gwei_from_url(url, speed_string)


def get_gas_price_ftm(speed):
    web3 = Chain().get_w3()
    gas_price = int(web3.fromWei(web3.eth.gas_price, 'gwei'))
    if speed == SPEED_STANDARD:
        return gas_price
    elif speed == SPEED_FAST:
        return int(gas_price * 108 / 100)
    elif speed == SPEED_URGENT:
        return int(gas_price * 120 / 100)
    else:
        raise Exception(f"[?] Couldn't get speed {speed} for FTM")


def get_gas_price_ftm_site(speed):
    speed_string = None
    if speed == SPEED_STANDARD:
        speed_string = "standardgas"
    elif speed == SPEED_FAST:
        speed_string = "fastgas"
    elif speed == SPEED_URGENT:
        speed_string = "rapidgas"

    url = "https://ftmscan.com/gastracker"
    return get_gwei_from_url(url, speed_string)


def get_gas_price_matic_site(speed):
    speed_string = None
    if speed == SPEED_STANDARD:
        speed_string = "standardgas"
    elif speed == SPEED_FAST:
        speed_string = "fastgas"
    elif speed == SPEED_URGENT:
        speed_string = "rapidgas"

    url = "https://polygonscan.com/gastracker"
    return get_gwei_from_url(url, speed_string)


def get_gas_price_eth(speed):
    speed_string = None
    if speed == SPEED_STANDARD:
        speed_string = "safeLow"
    elif speed == SPEED_FAST:
        speed_string = "average"
    elif speed == SPEED_URGENT:
        speed_string = "fast"

    gas_data = requests.get("https://ethgasstation.info/api/ethgasAPI.json")
    if gas_data.status_code != 200:
        raise Exception("[?] ethGasStation Endpoint error | Status: {}".format(gas_data.status_code))
    gas_data = gas_data.json()

    return gas_data[speed_string] / 10


def get_gas_price_eth_long(speed):
    web3 = Chain().get_w3()
    web3.middleware_onion.add(middleware.simple_cache_middleware)  # quickest
    # web3.middleware_onion.add(middleware.time_based_cache_middleware)
    # web3.middleware_onion.add(middleware.latest_block_based_cache_middleware)

    if speed == SPEED_STANDARD:
        web3.eth.set_gas_price_strategy(slow_gas_price_strategy)
    elif speed == SPEED_FAST:
        web3.eth.set_gas_price_strategy(medium_gas_price_strategy)
    elif speed == SPEED_URGENT:
        web3.eth.set_gas_price_strategy(fast_gas_price_strategy)

    web3.eth.generate_gas_price()

    return int(web3.fromWei(web3.eth.gas_price, 'gwei'))


def get_gas_price_eth_site(speed):
    speed_string = None
    if speed == SPEED_STANDARD:
        speed_string = "spanLowPrice"
    elif speed == SPEED_FAST:
        speed_string = "spanAvgPrice"
    elif speed == SPEED_URGENT:
        speed_string = "spanHighPrice"

    url = "https://etherscan.io/gastracker"
    return get_gwei_from_url(url, speed_string)


def get_gwei_from_url(url, speed_string):
    session = requests.Session()
    session.headers.update({'User-Agent':
                                'Mozilla/5.0 (X11; Linux i686 on x86_64) '
                                'AppleWebKit/537.36 (KHTML, like Gecko) '
                                'Chrome/55.0.2909.25 Safari/537.36'})
    gas_data = session.get(url)

    if gas_data.status_code != 200:
        raise Exception("[?] {} Endpoint error | Status: {}".format(url, gas_data.status_code))
    root = html.fromstring(gas_data.content)
    for sel in root.xpath(f"//span[contains(@id, '{speed_string}')]"):
        if sel.text:
            s = sel.text.strip()
            if s.isdigit():  # https://etherscan.io/gastracker version
                return s
            if len(s) > 3:  # other /gastracker versions
                txt = textwrap.fill(s, width=50)
                for word in txt.split():
                    number = word.replace(".", "", 1)  # replace decimals if they exist
                    if number.isdigit():
                        return int(float(word))
    raise Exception("[?] Couldn't get {} speed from {}".format(speed_string, url))


def get_gas_price_avax(speed):
    web3 = Chain().get_w3()
    gas_price = int(web3.fromWei(web3.eth.gas_price, 'gwei'))
    if speed == SPEED_STANDARD:
        return gas_price
    elif speed == SPEED_FAST:
        return int(gas_price * 108 / 100)
    elif speed == SPEED_URGENT:
        return int(gas_price * 120 / 100)
    else:
        raise Exception(f"[?] Couldn't get speed {speed} for AVAX")


def main():
    network = const.AVAX
    web3 = Chain(network).get_w3()
    print(f"\tdefault: {int(web3.fromWei(web3.eth.gas_price, 'gwei'))} gwei")
    print(f"\t{SPEED_STANDARD} speed: {get_gas_price(SPEED_STANDARD)}")
    print(f"\t{SPEED_FAST} speed: {get_gas_price(SPEED_FAST)}")
    print(f"\t{SPEED_URGENT} speed: {get_gas_price(SPEED_URGENT)}")

    # GAS_SPEED = SPEED_STANDARD
    # GAS_SPEED = SPEED_FAST
    # GAS_SPEED = SPEED_URGENT
    # for i in chains.chain_list:
    #     network = i
    #     web3 = connect(network)
    #     # network_data = chains.getNetworkData(i)
    #     # data.showNetworkInfo(network_data)
    #     print(f"[+] Gas price for:")
    #     print(f"\tdefault: {int(web3.fromWei(web3.eth.gas_price, 'gwei'))} gwei")
    #     print(f"\t{SPEED_URGENT} speed: {get_gas_price(web3, network, SPEED_URGENT)}")
    #     print(f"\t{SPEED_FAST} speed: {get_gas_price(web3, network, SPEED_FAST)}")
    #     print(f"\t{SPEED_STANDARD} speed: {get_gas_price(web3, network, SPEED_STANDARD)}")


if __name__ == "__main__":
    main()
