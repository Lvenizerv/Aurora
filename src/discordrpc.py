from pypresence import Presence
import time
import json
from src.frontend import *

try:
    CONFIG = json.load(open("config.json", "r"))
except FileNotFoundError:
    fatal("Aurora could not find 'config.json'!")
    close()
    
client_id = 968684778490593370
RPC = Presence(client_id)
RPC.connect()

def updateStatus(status):
    if CONFIG["discordRPC"] == True:
        RPC.update(
            buttons =
            [
                {
                    "label": "Aurora Website", 
                    "url": "https://www.auroratools.shop/"
                }, 
                {
                    "label": "Aurora Server", 
                    "url": "https://discord.gg/auroramultitool"
                }
            ],
            large_image = "logo", 
            large_text = "Aurora Multitool", 
            details = status,
            start=time.time()
        )