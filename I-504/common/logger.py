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
        print(Back.LIGHTGREEN_EX + "[SUCC ]" + Back.RESET + Fore.LIGHTGREEN_EX + f" {self.tag}:\t {msg}" + Fore.RESET)

    def info(self, msg:str):
        print(Back.LIGHTBLUE_EX + "[INFO ]" + Back.RESET + Fore.LIGHTBLUE_EX + f" {self.tag}:\t {msg}" + Fore.RESET)

    def warn(self, msg:str):
        print(Back.YELLOW + "[WARN ]" + Back.RESET + Fore.YELLOW + f" {self.tag}:\t {msg}" + Fore.RESET)

    def error(self, msg:str):
        print(Back.RED + "[ERROR]" + Back.RESET + Fore.RED + f" {self.tag}:\t {msg}" + Fore.RESET)

    def fatal(self, msg:str):
        print(Back.RED + "[FATAL]" + f" {self.tag}:\t {msg}" + Back.RESET)

    def child(self, child_tag:str):
        return Logger(f"{self.tag}/{child_tag}")




