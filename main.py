# Project Swiss (Aurora 2)
# Property of auroratools.shop

# login - line 14

### Imports ###

import os
import json
import time
import requests
import sys

from soupsieve import select

import src.discordrpc as discordrpc
from src.frontend import *
from src.endpoints import auth
from src.roblox import api, botting, tools

### Code ###

VERSION = "2.3.4"
header = f"""


 ▄▄▄       █    ██  ██▀███   ▒█████   ██▀███   ▄▄▄         
▒████▄     ██  ▓██▒▓██ ▒ ██▒▒██▒  ██▒▓██ ▒ ██▒▒████▄       
▒██  ▀█▄  ▓██  ▒██░▓██ ░▄█ ▒▒██░  ██▒▓██ ░▄█ ▒▒██  ▀█▄     
░██▄▄▄▄██ ▓▓█  ░██░▒██▀▀█▄  ▒██   ██░▒██▀▀█▄  ░██▄▄▄▄██    
 ▓█   ▓██▒▒▒█████▓ ░██▓ ▒██▒░ ████▓▒░░██▓ ▒██▒ ▓█   ▓██▒   
 ▒▒   ▓▒█░░▒▓▒ ▒ ▒ ░ ▒▓ ░▒▓░░ ▒░▒░▒░ ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░   
  ▒   ▒▒ ░░░▒░ ░ ░   ░▒ ░ ▒░  ░ ▒ ▒░   ░▒ ░ ▒░  ▒   ▒▒ ░   
  ░   ▒    ░░░ ░ ░   ░░   ░ ░ ░ ░ ▒    ░░   ░   ░   ▒      
      ░  ░   ░        ░         ░ ░     ░           ░  ░  

auroratools.shop | version {VERSION} | discord.gg/auroramultitool
"""

menu = """
┌─tools─────────────────────────────────────────────────────────────────────────────────┐
│  [ 01 ] Model Bot           [ 09 ] Follow Bot          [ 17 ] Game Dislike Bot        │
│  [ 02 ] Cookie Generator    [ 10 ] Comob2Cookie        [ 18 ] Display Name Changer    │
│  [ 03 ] Cookie Checker      [ 11 ] UPC2Cookie          [ 19 ] Report Bot              │
│  [ 04 ] Favorite Bot        [ 12 ] Email Verifier      [ 20 ] Shirt Id Scraper        │
│  [ 05 ] Shirt Downloader    [ 13 ] Cookie Refresher    [ 21 ] Proxy Checker           │
│  [ 06 ] Mass Shirt DL       [ 14 ] Region Changer      [ 22 ] Cookie Killer           │
│  [ 07 ] Group Finder        [ 15 ] Visit Bot           [ 23 ] Group Username Scraper  │
│  [ 08 ] Friend Req Bot      [ 16 ] Game Like Bot       [ 24 ] Status Changer          │
└───────────────────────────────────────────────────────────────────────────────────────┘
┌─other────────┐     ┌─support─────────┐
│  [ 0 ] Exit  │     │  [ C ] Credits  │
└──────────────┘     └─────────────────┘
"""

clear()
setTitle("Aurora II | Starting")

# login
log("Authorizing...")

#license check
with open('license.txt','r') as f:
    try:
        authentication = auth(f.readlines()[0])
    except:
        authentication = auth(inp('Enter license: '), False)
try:
    if authentication['bool'] == False:
        fatal("You are not authorized to use this software.")
        fatal(f"-> {authentication['answer']}")
        log("You can buy a license @ auroratools.shop")
        close()
except Exception:
    pass

# check for updates
log("Checking for updates...")
try:
    upd = requests.get("https://api.auroratools.shop/data.json")
    if VERSION != upd.json()["version"]:
        log(f"There is an update available ({VERSION} -> {upd.json()['version']})")
        if yn('Would you like to download update?'):
            os.system(f"start update.exe")
            sys.exit()
except Exception as e:
    warn(f"Could not check for updates ({e})!")
    log("Please join the Discord (discord.gg/auroramultitool) and report this.")
    pause()

# config reading
log("Reading configuration file...")
try:
    CONFIG = json.load(open("config.json", "r"))
except FileNotFoundError:
    fatal("Aurora could not find 'config.json'!")
    close()
ok("Config loaded!")

# startup options
if CONFIG["checkCookiesOnStart"] == True: # CHECK COOKIES ON START
    try:
        log("Checking your cookies...")
        co = [botting.Cookie(ck) for ck in open("cookies.txt", "r").read().splitlines()]
        new = api.checkAll(co)
        with open("cookies.txt", 'w') as f:
            f.write("")
        with open("cookies.txt", "a") as f:
            for c in new:
                f.write(c + "\n")
        ok(f"Checked all cookies ({len(new)}/{len(co)})!")
    except FileNotFoundError:
        fatal("Aurora could not find your cookies file!")
        close()

# cookie & proxy reading
try:
    cookies = [botting.Cookie(ck) for ck in open("cookies.txt", "r").read().splitlines()]
    proxies = open("proxies.txt", "r").read().splitlines()
except FileNotFoundError:
    fatal("Aurora could not find your cookies or proxies file!")
    close()
ok(f"Loaded {len(cookies)} cookies & {len(proxies)} proxies!")
if CONFIG["discordRPC"] == True:
    discordrpc.updateStatus("Browsing the Main Menu")


# MENU 
while True:
    clear()
    setTitle("Aurora II | Main Menu")
    api.setWindowsPolicy()
    
    for line in header.splitlines():
        print(line.center(os.get_terminal_size().columns))

    for line in menu.splitlines():
        print(line.center(os.get_terminal_size().columns))
    
    if len(cookies) == 0 or len(proxies) == 0:
        print()
        fatal("You do not have any cookies (and or) proxies! Please add some and restart.")
        hint("Confused? You can read the documentation @ docs.auroratools.shop")
        close()

    try:
        selection = input("                 " + selector)
    except ValueError:
        continue

    if selection == "1":
        discordrpc.updateStatus("Botting Models")
        tools.modelBot(cookies, proxies)
        
    elif selection == "2":
        discordrpc.updateStatus("Generating Cookies")
        tools.cookieGen(proxies, CONFIG["captchaSettings"])

    elif selection == "3":
        discordrpc.updateStatus("Checking Cookies")
        tools.cookieChecker()

    elif selection == "4":
        discordrpc.updateStatus("Botting Favorites")
        tools.favoriteBot(cookies, proxies)

    elif selection == "5":
        discordrpc.updateStatus("Downloading Shirt")
        tools.shirtDownloader(proxies)

    elif selection == "6":
        discordrpc.updateStatus("Mass Downloading Shirts")
        tools.massShirtDownloader(proxies)

    elif selection == "7":
        discordrpc.updateStatus("Finding Groups")
        tools.groupFinder(proxies, CONFIG["captchaSettings"])
    
    elif selection == "8":
        discordrpc.updateStatus("Botting Friend Requests")
        tools.friendBot(cookies)
    
    elif selection == "9":
        discordrpc.updateStatus("Botting Follows")
        tools.followBot(cookies, proxies, CONFIG["captchaSettings"])
    
    elif selection == "10":
        discordrpc.updateStatus("Turning Combos into Cookies")
        tools.combo2Cookie(cookies, proxies, CONFIG["captchaSettings"])
    
    elif selection == "11":
        discordrpc.updateStatus("Turning UPC into Cookies")
        tools.upc2Cookie(cookies)

    elif selection == "12":
        discordrpc.updateStatus("Verifying Email")
        tools.emailVerify(cookies, proxies)
        
    elif selection == "13":
        discordrpc.updateStatus("Refreshing Cookies")
        tools.cookieRefresher(cookies, proxies)
    
    elif selection == "14":
        discordrpc.updateStatus("Changing Region")
        tools.regionChange(cookies, proxies)
    
    elif selection == "15":
        discordrpc.updateStatus("Botting Games")
        tools.visitBot(cookies)
       
    elif selection == "16":
        discordrpc.updateStatus("Liking Games")
        tools.likeBot(cookies)
       
    elif selection == "17":
        discordrpc.updateStatus("Disliking Games")
        tools.dislikeBot(cookies)
       
    elif selection == "18":
        discordrpc.updateStatus("Changing Display Names")
        tools.displayChanger(cookies, proxies)
    
    elif selection == "19":
        discordrpc.updateStatus("Reporting Users")
        tools.reportBot(cookies)

    elif selection == "20":
        discordrpc.updateStatus("Scraping Shirts")
        tools.shirtIdScraper(proxies)
       
    elif selection == "21":
        discordrpc.updateStatus("Checking Proxies")
        tools.proxyChecker(proxies)
    
    elif selection == "22":
        discordrpc.updateStatus("Cookie Killer")
        tools.cookieKiller(cookies, proxies)

    elif selection == "23":
        discordrpc.updateStatus("Scraping Usernames From Groups")
        tools.groupUsernameScraper()

    elif selection == "24":
        discordrpc.updateStatus("Changing Statuses")
        tools.statusChanger(cookies, proxies)

    elif selection.lower() == "c":
        discordrpc.updateStatus("Browsing Credits")
        tools.credits()
