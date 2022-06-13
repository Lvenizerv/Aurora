import os
import ctypes
import sys
import json
from datetime import datetime
from colorama import Fore, Style

CONFIG = json.load(open("config.json", "r"))

def setTitle(title: str):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def clear():
    if 'nt' in os.name:
        os.system('cls')
    else:
        os.system('clear')

def timet():
    if CONFIG['use12HourClock']:
        return Style.BRIGHT + Fore.BLACK + f"    [{datetime.now().strftime('%I:%M')}]  "    
    else:
        return Style.BRIGHT + Fore.BLACK + f"    [{datetime.now().strftime('%H:%M')}]  "

selector = f"{Style.BRIGHT}{Fore.MAGENTA}>{Fore.BLUE}>{Fore.CYAN}>{Fore.LIGHTGREEN_EX}>{Fore.WHITE}  "

def inp(query):
    x = input(timet() + f"      {Style.BRIGHT}{Fore.WHITE}{query}  {selector}")

    return x

def log(object):
    print(timet() + f"{Style.BRIGHT}{Fore.MAGENTA}LOG   {Fore.WHITE}{object}")

def ok(object):
    print(timet() + f"{Style.BRIGHT}{Fore.GREEN}OKAY  {Fore.WHITE}{object}")

def fatal(object):
    print(timet() + f"{Style.BRIGHT}{Fore.RED}ERR!  {Fore.WHITE}{object}")

def warn(object):
    print(timet() + f"{Style.RESET_ALL}{Fore.YELLOW}WARN  {Style.BRIGHT}{Fore.WHITE}{object}")

def yn(query):
    while True:
        x = input(timet() + f"      {Style.BRIGHT}{Fore.WHITE}{query} [{Fore.GREEN}y{Fore.WHITE}/{Fore.RED}n{Fore.WHITE}]  {selector}")
        if x == 'y' or x == 'Y':
            return True
        elif x == 'n' or x == 'N':
            return False
        else:
            warn("Please provide a valid answer.")

def hint(object):
    print(timet() + f"{Style.BRIGHT}{Fore.BLUE}HINT  {Fore.WHITE}{object}")

def close():
    input(timet() + f"      {Style.BRIGHT}{Fore.BLACK}Press [ ENTER ] to close.{Fore.RESET}")
    sys.exit()

def pause():
    input(timet() + f"      {Style.BRIGHT}{Fore.BLACK}Press [ ENTER ] to return.{Fore.RESET}")