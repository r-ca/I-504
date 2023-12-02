# LOGGER

from colorama import Fore, Back, Style

is_debug = True

class Logger:
    def __init__(self, tag:str):
        self.tag = tag

    def debug(self, msg:str):
        if is_debug:
            print(Style.DIM + f"[DEBUG] {self.tag}:\t {msg}" + Style.RESET_ALL)

    def succ(self, msg:str):
        print(Fore.LIGHTGREEN_EX + "[SUCC ]" + Fore.RESET + f" {self.tag}:\t {msg}")

    def info(self, msg:str):
        print(Fore.LIGHTBLUE_EX + "[INFO ]" + Fore.RESET + f" {self.tag}:\t {msg}")

    def warn(self, msg:str):
        print(Fore.YELLOW + "[WARN ]" + Fore.RESET + f" {self.tag}:\t {msg}")

    def error(self, msg:str):
        print(Fore.RED + "[ERROR]" + Fore.RESET + f" {self.tag}:\t {msg}")

    def fatal(self, msg:str):
        print(Back.RED + "[FATAL]" + Back.RESET + f" {self.tag}:\t {msg}")

    def child(self, child_tag:str):
        return Logger(f"{self.tag}/{child_tag}")




