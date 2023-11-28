# LOGGER

is_debug = True

class Logger:
    def __init__(self, tag:str):
        self.tag = tag

    def debug(self, msg:str):
        if is_debug:
            print(f"[DEBUG] {self.tag}:\t {msg}")

    def info(self, msg:str):
        print(f"[INFO] {self.tag}:\t {msg}")

    def warn(self, msg:str):
        print(f"[WARN] {self.tag}:\t {msg}")

    def error(self, msg:str):
        print(f"[ERROR] {self.tag}:\t {msg}")

    def fatal(self, msg:str):
        print(f"[FATAL] {self.tag}:\t {msg}")

    def child(self, child_tag:str):
        return Logger(f"{self.tag}/{child_tag}")




