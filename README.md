# pecunia_ad_vitam

#### v2.0 by Bogdan Vaida (contact@vaidabogdan.com)

My very own DEX trading tool.

You can create an account on [Pushsafer.com]() and use the API key to get notified on various devices.

Or just use "sudo apt-get install gnustep-gui-runtime" (or the native mac 'say') to get a verbal cue.

# Usage

You can use it by modifying config.py (without arguments) or using commandline arguments.

# Example

./pecunia_ad_vitam.py -h

pecunia_ad_vitam.py -n network [-r router] -w wallet -t token -d token-dest --swap -a amount --dump --speed speed --approve --wait seconds --slippage amount -v --pushsafer -p -h
pecunia_ad_vitam.py --encrypt

If there are no arguments it will take the values from config.py

Usage:
        -n network is one of these: eth/ropsten/bsc/chapel/polygon/avax/ftm
        -r uniswap/pancakeswap/quickswap/traderjoe/apeswap/spiritswap/spookyswap * uniswap v3, pancakeswap & apeswap v2
        -a amount is the number of tokens to swap (float)
        --swap will activate swapping which required a destination token and an amount or the dump option
        --dump dumps the token
        --speed standard/fast/urgent for the gas speed
        --approve will approve the token transaction
        --wait seconds will wait for token to appear in wallet and check every X seconds
        --slippage 1-100
        -v will use system's voice to announce the transaction
        --pushsafer will use Pushsafer to announce the transaction
        -p will initiate a password input
        --encrypt will encrypt a private key and display it to add to the config file

./pecunia_ad_vitam.py -n bsc -w MYWALLET -t MYTOKEN -d LIQUIDITYPAIR --swap -a 5 --approve --slippage 15 --pushsafer --wait 1


# Disclaimer

Use it at your own risk and definitely try it out with a new wallet address. Not thoroughly tested on ERC20 and Fantom.
This code is available for anyone with a bit of python skills, you need to be able to go once through it to know how everything functions.
I'm not a programmer at heart, just wanted to code the tools I needed for my work.