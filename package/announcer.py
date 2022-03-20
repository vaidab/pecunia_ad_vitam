import os
from getpass import getpass

import package.pushsafer as pushsafer
from package.classes import Singleton


class Announcer(metaclass=Singleton):
    def __init__(self, use_pushsafer=None, pushsafer_key=None, use_voice=None):
        self.use_pushsafer = use_pushsafer
        self.use_voice = use_voice

        if use_pushsafer:
            if pushsafer_key:
                self.pushsafer_key = pushsafer_key
            else:
                self.pushsafer_key = getpass(prompt="[+] Input Pushsafer key: ")

    def pushsafer(self, msg):
        if self.use_pushsafer:
            pushsafer.alert(msg, self.pushsafer_key)

    def voice(self, msg):
        if self.use_voice:
            os.system(f'say "{msg}"')

    def print_and_voice(self, msg):
        print(msg)
        self.voice(msg)


    def all(self, msg):
        print(msg)
        self.voice(msg)
        self.pushsafer(msg)
