import asyncio
import random
from tkinter.messagebox import NO
from weakref import proxy
from click import group
from rstr import xeger
from datetime import datetime

from src.roblox.api import conGather
from src.roblox.botting import *
from src.frontend import *

# these should be designed to just pause before they're done, dont close out
def setup():
    clear()
    print("\n")
    hint("Need help? docs.auroratools.shop")

def favoriteBot(cookies: list[Cookie], proxies: list):
    setTitle("Aurora II | Favorite Bot")
    setup()

    warn("This tool uses an API that toggles the favorite, meaning if")
    warn("you are using the same cookies, you may lose favorites.")

    while True:
        try:
            amount = int(inp("Amount"))
            break
        except ValueError:
            warn("Please enter a number.")

    while True:
        try:
            loop = asyncio.get_event_loop()
            asset = int(inp("Asset ID"))
            assetInfo = loop.run_until_complete(getAssetInformation(asset))
            # locked kwargs
            scheme = {
                "assetId": assetInfo["TargetId"],
                "productId": assetInfo["ProductId"],
                "creatorId": assetInfo["Creator"]["Id"]
            }
            break
        except ValueError:
            warn("Please enter a number.")
        except KeyError:
            warn(f"Failed to retrieve data for '{asset}', please try another.")

    log("Setting up...")
    coros = []
    temp = cookies

    for _ in range(amount):
        c = random.choice(temp)
        temp.remove(c)
        coros.append(c.favorite(random.choice(proxies), asset))

    log("Finished setup...")
    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))
    pause()

def groupFinder(proxies, config):
    setTitle("Aurora II | Group Finder")
    setup()

    # claim = yn("Do you want to automatically claim groups?")

    # if claim == True:
    #     if config['service'] == "" or config['apiKey'] == "":
    #         fatal("You cannot use this tool without setting up captcha settings in config.")
    #         hint("You can refer to the documentation if you're confused.")
    #         pause()
    #         return None

    #     log(f"You're using {config['service']}.")
    #     log(f"Your API key for this service is: {config['apiKey']}")
        
    #     cookie = inp("Your cookie (to claim groups)")

    while True:
        range_ = inp("Range ex: 123456-223456")
        try:
            low, high = range_.split("-")
            if len(range_.split("-")) > 2:
                raise Exception
            if int(low) >= int(high):
                warn("The low value is more than or equal to the high value.")
            else:
                low, high = int(low), int(high)
                break
        except Exception as e:
            warn("Please follow the example, include a dash or make sure you're including numbers.")

    log("Setting up...")
    coros = [checkGroup(i, random.choice(proxies)) for i in range(low, high)]
    log("Finished setup...")

    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))
    log("Finished!")
    pause()

def modelBot(cookies: list[Cookie], proxies: list):
    setTitle("Aurora II | Model Bot")
    setup()
    
    while True:
        try:
            amount = int(inp("Amount"))
            break
        except ValueError:
            warn("Please enter a number.")

    while True:
        try:
            loop = asyncio.get_event_loop()
            asset = int(inp("Asset ID"))
            assetInfo = loop.run_until_complete(getAssetInformation(asset))
            # locked kwargs
            scheme = {
                "assetId": assetInfo["TargetId"],
                "productId": assetInfo["ProductId"],
                "creatorId": assetInfo["Creator"]["Id"]
            }
            break
        except ValueError:
            warn("Please enter a number.")
        except KeyError:
            warn(f"Failed to retrieve data for '{asset}', please try another.")

    log("Setting up...")
    coros = [random.choice(cookies).botAsset(random.choice(proxies), **scheme) for i in range(0, amount)]
    log("Finished setup...")

    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))
    log("Finished!")
    pause()

def cookieGen(proxies, config):
    setTitle("Aurora II | Cookie Generator")
    setup()

    while True:
        exp = inp("Username RegEx")
        log(f"Example usernames: {xeger(exp)}, {xeger(exp)}")
        if yn("Are you sure?") == True:
            break
    
    password = inp("Password (for all cookies)")
    while True:
        try:
            amount = int(inp("Amount"))
            break
        except ValueError:
            warn("Please enter a number.")

    while True:
        try:
            loc = inp("Out File (leave blank to generate one)")
            if loc == "":
                loc = f"aurora-{datetime.now().strftime('%m_%d_%y-%I_%M.txt')}"
            if ".txt" not in loc:
                loc += '.txt'
            open(loc, "x")
            open(loc, 'w').write("### Generated with Aurora II | novuh.dev/botting ###\n")
            break
        except FileExistsError:
            warn("A file with that name already exists.")
        except Exception as e:
            warn(f"Please try again. {e}")

    log("Setting up...")
    coros = [generateCookie(loc, xeger(exp), password, config['service'], config['apiKey'], config['maxRetries'], random.choice(proxies)) for i in range(0, amount)]
    log("Finished setup...")

    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))

    log("Finished!")
    log(f"You can find your cookies in '{loc}'.")
    pause()

def cookieChecker():
    setup()
    setTitle("Aurora II | Cookie Checker")

    while True:
        try:
            file = inp("Cookie File (leave blank for default)")
            if file == "":
                file = "cookies.txt"
            elif ".txt" not in file:
                file += ".txt"

            unchecked = [Cookie(c) for c in open(file, "r").read().splitlines()]
            log(f"Loaded {len(unchecked)} cookies.")
            break
        except FileNotFoundError:
            warn("Aurora could not find that file, please try again.")

    log("Setting up...")
    coros = [c.check() for c in unchecked]
    log("Finished setup...")

    log("Running...")
    loop = asyncio.get_event_loop()
    new = list(filter(None, loop.run_until_complete(conGather(*coros))))

    with open(file, 'w') as f:
        f.write("")
    with open(file, "a") as f:
        for c in new:
            f.write(c + "\n")

    log("Finished!")
    hint("Your invalid cookies have been removed from the original file.")
    pause()

def shirtDownloader(proxies):
    setTitle("Aurora II | Shirt Downloader")
    setup()

    while True:
        try:
            id = int(inp("Shirt ID"))
            break
        except ValueError:
            warn("Please input a number.")
    
    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(downloadShirt(id, random.choice(proxies)))
    log("Finished!")
    pause()

def massShirtDownloader(proxies):
    setTitle("Aurora II | Mass Shirt Downloader")
    setup()

    while True:
        try:
            file = inp("Shirt ID file")

            if ".txt" not in file:
                file += ".txt"

            shirts = []
            for shirt in open(file, 'r').read().splitlines():
                try:
                    shirts.append(int(shirt))
                except ValueError:
                    pass
            
            log(f"Loaded {len(shirts)} shirt ids.")
            break
        except FileNotFoundError:
            warn("Aurora could not find that file, please try again.")

    log("Setting up...")
    coros = [downloadShirt(id, random.choice(proxies)) for id in shirts]
    log("Finished setup...")

    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))
    log("Finished!")
    pause()

def shirtIdScraper(proxies):
    setTitle("Aurora II | Shirt ID Scraper")
    setup()  
    while True:
        try:
            file = inp("Shirt File")

            if ".txt" not in file:
                file += ".txt"

            break
        except FileNotFoundError:
            warn("Aurora could not find that file, please try again.")
    running = True
    nextcursor = ""
    while running:
        loop = asyncio.get_event_loop()
        cursor = loop.run_until_complete(scrapeShirts(file, random.choice(proxies), nextcursor))
        if cursor != None:
            nextcursor = cursor
        else:
            running = False
    log("Finished!")
    pause()
            

def friendBot(cookies):
    setTitle("Aurora II | Friend Req. Bot")
    setup()

    while True:
        try:
            amount = int(inp("Amount"))
            break
        except ValueError:
            warn("Please enter a number.")
    
    while True:
        try:
            target = int(inp("Target User ID"))
            break
        except ValueError:
            warn("Please enter a number.")

    log("Setting up...")
    coros = [random.choice(cookies).friend(target) for i in range(amount)]
    log("Finished setting up!")
    
    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))
    log("Finished!")
    pause()

def followBot(cookies, proxies, config):
    setTitle("Aurora II | Follow Bot")
    setup()

    while True:
        try:
            amount = int(inp("Amount"))
            break
        except ValueError:
            warn("Please enter a number.")
    
    while True:
        try:
            target = int(inp("Target User ID"))
            break
        except ValueError:
            warn("Please enter a number.")

    log("Setting up...")
    coros = [random.choice(cookies).follow(target, config['service'], config['apiKey'], config['maxRetries'], random.choice(proxies)) for i in range(amount)]
    log("Finished setting up!")
    
    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))
    log("Finished!")
    pause()

def combo2Cookie(cookies, proxies, config):
    setTitle("Aurora II | Combo 2 Cookie")
    setup()
    while True:
        try:
            loc = inp("Out File (leave blank to generate one)")
            if loc == "":
                loc = f"aurora-{datetime.now().strftime('%m_%d_%y-%I_%M.txt')}"
            if ".txt" not in loc:
                loc += '.txt'
            open(loc, "x")
            open(loc, 'w').write("### Converted with Aurora II | novuh.dev/botting ###\n")
            cookies = [Cookie(c) for c in open("cookies.txt", "r").read().splitlines()]
            log(f"Loaded {len(cookies)} accounts.")
            break
        except FileExistsError:
            warn("A file with that name already exists.")
        except Exception as e:
            warn(f"Please try again. {e}")

    log("Setting up...")
    coros = [c.loginUP(loc, config['service'], config['apiKey'], config['maxRetries'], random.choice(proxies)) for c in cookies]
    log("Finished setup...")

    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))

    log("Finished!")
    log(f"You can find your cookies in '{loc}'.")
    pause()

def upc2Cookie(cookies):
    setTitle("Aurora II | UPC 2 Cookie")
    setup()
    while True:
        try:
            loc = inp("Out File (leave blank to generate one)")
            if loc == "":
                loc = f"aurora-{datetime.now().strftime('%m_%d_%y-%I_%M.txt')}"
            if ".txt" not in loc:
                loc += '.txt'
            open(loc, "x")
            open(loc, 'w').write("### Converted with Aurora II | novuh.dev/botting ###\n")
            cookies = [Cookie(c) for c in open("cookies.txt", "r").read().splitlines()]
            log(f"Loaded {len(cookies)} cookies.")
            break
        except FileExistsError:
            warn("A file with that name already exists.")
        except Exception as e:
            warn(f"Please try again. {e}")

    log("Setting up...")
    coros = [c.upc2Cookie(loc) for c in cookies]
    log("Finished setup...")

    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))

    log("Finished!")
    log(f"You can find your cookies in '{loc}'.")
    pause()

def emailVerify(cookies, proxies):
    setTitle("Aurora II | Email Verifier")
    setup()

    while True:
        try:
            loc = inp("Out File (leave blank to generate one)")
            if loc == "":
                loc = f"aurora-{datetime.now().strftime('%m_%d_%y-%I_%M.txt')}"
            if ".txt" not in loc:
                loc += '.txt'
            open(loc, "x")
            open(loc, 'w').write("### Verified with Aurora II | auroratools.shop ###\n")
            break
        except FileExistsError:
            warn("A file with that name already exists.")
        except Exception as e:
            warn(f"Please try again. {e}")

    log("Setting up...")
    coros = [c.verify(loc, random.choice(proxies)) for c in cookies]
    log("Finished setup...")

    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))

    log("Finished!")
    log(f"You can find your cookies in '{loc}'.")
    pause()

def cookieRefresher(cookies, proxies):
    setTitle("Aurora II | Cookie Refresher")
    setup()

    while True:
        try:
            loc = inp("Out File (leave blank to generate one)")
            if loc == "":
                loc = f"aurora-{datetime.now().strftime('%m_%d_%y-%I_%M.txt')}"
            if ".txt" not in loc:
                loc += '.txt'
            open(loc, "x")
            open(loc, 'w').write("### Refreshed with Aurora II | auroratools.shop ###\n")
            break
        except FileExistsError:
            warn("A file with that name already exists.")
        except Exception as e:
            warn(f"Please try again. {e}")

    log("Setting up...")
    coros = [c.refreshCookie(loc, random.choice(proxies)) for c in cookies]
    log("Finished setup...")

    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))

    log("Finished!")
    log(f"You can find your cookies in '{loc}'.")
    pause()

def displayChanger(cookies, proxies):
    setTitle("Aurora II | Display Name Changer")
    setup()

    while True:
        try:
            name = inp("Target Display Name")
            break
        except Exception as e:
            warn(f"Please try again. {e}")

    log("Setting up...")
    coros = [c.changeDisplay(name, random.choice(proxies)) for c in cookies]
    log("Finished setup...")

    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))

    log("Finished!")
    pause()

def visitBot(cookies):
    setTitle("Aurora II | Visit Bot")
    setup()

    while True:
        try:
            gameId = inp("Target Game Id")
            break
        except Exception as e:
            warn(f"Please try again. {e}")

    log("Setting up...")
    coros = [c.visitGame(gameId) for c in cookies]
    log("Finished setup...")

    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))

    log("Finished!")
    pause()

def likeBot(cookies):
    setTitle("Aurora II | Like Bot")
    setup()

    while True:
        try:
            gameId = inp("Target Game Id")
            break
        except Exception as e:
            warn(f"Please try again. {e}")

    log("Setting up...")
    coros = [c.rateGame(gameId, True) for c in cookies]
    log("Finished setup...")

    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))

    log("Finished!")
    pause()

def dislikeBot(cookies):
    setTitle("Aurora II | Dislike Bot")
    setup()

    while True:
        try:
            gameId = inp("Target Game Id")
            break
        except Exception as e:
            warn(f"Please try again. {e}")

    log("Setting up...")
    coros = [c.rateGame(gameId, False) for c in cookies]
    log("Finished setup...")

    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))

    log("Finished!")
    pause()

def reportBot(cookies):
    setTitle("Aurora II | Report Bot")
    setup()

    while True:
        try:
            userId = inp("Target User Id")
            break
        except Exception as e:
            warn(f"Please try again. {e}")

    log("Setting up...")
    coros = [c.reportUser(userId) for c in cookies]
    log("Finished setup...")

    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))

    log("Finished!")
    pause()

def regionChange(cookies, proxies):
    setTitle("Aurora II | Region Change")
    setup()
    
    while True:
        try:
            loc = inp("Out File (leave blank to generate one)")
            if loc == "":
                loc = f"aurora-{datetime.now().strftime('%m_%d_%y-%I_%M.txt')}"
            if ".txt" not in loc:
                loc += '.txt'
            open(loc, "x")
            open(loc, 'w').write("### Changed with Aurora II | auroratools.shop ###\n")
            break
        except FileExistsError:
            warn("A file with that name already exists.")
        except Exception as e:
            warn(f"Please try again. {e}")
    log("Setting up...")    
    coros = [c.regionChange(loc, random.choice(proxies)) for c in cookies]
    log("Finished setup...")
    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))

    log("Finished!")
    log(f"You can find your cookies in '{loc}'.")
    pause()
    
def proxyChecker(proxies):
    setTitle("Aurora II | Proxy Checker")
    setup()
    
    while True:
        try:
            loc = inp("Out File (leave blank to generate one)")
            if loc == "":
                loc = f"aurora-{datetime.now().strftime('%m_%d_%y-%I_%M.txt')}"
            if ".txt" not in loc:
                loc += '.txt'
            open(loc, "x")
            open(loc, 'w').write("### Checked with Aurora II | auroratools.shop ###\n")
            break
        except FileExistsError:
            warn("A file with that name already exists.")
        except Exception as e:
            warn(f"Please try again. {e}")
    log("Setting up...")    
    coros = [proxyCheck(loc, random.choice(proxies)) for p in proxies]
    log("Finished setup...")
    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))

    log("Finished!")
    log(f"You can find your working proxies in '{loc}'.")
    pause()

def cookieKiller(cookies, proxies):
    setTitle("Aurora II | Cookie Killer")
    setup()

    while True:
        try:
            file = inp("Cookie File (leave blank for default)")
            if file == "":
                file = "cookies.txt"
            elif ".txt" not in file:
                file += ".txt"

            cookies = [Cookie(c) for c in open(file, "r").read().splitlines()]
            log(f"Loaded {len(cookies)} cookies.")
            break
        except FileNotFoundError:
            warn("Aurora could not find that file, please try again.")

    log("Setting up...")
    coros = [c.kill(random.choice(proxies)) for c in cookies]
    log("Finished setup...")

    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))
    log("Finished!")
    pause()

def groupUsernameScraper():
        setTitle("Aurora II | Group Username Scraper")
        setup()
        
        while True:
            try:
                groupId = int(inp("Target Group ID"))
            except ValueError:
                warn("Please enter a number.") 
            try:
                loc = inp("Out File (leave blank to generate one)")
                if loc == "":
                    loc = f"aurora-{datetime.now().strftime('%m_%d_%y-%I_%M.txt')}"
                if ".txt" not in loc:
                    loc += '.txt'
                open(loc, "x")
                open(loc, 'w').write("### Scraped with Aurora II | auroratools.shop ###\n")
                break
            except FileExistsError:
                warn("A file with that name already exists.")
            except Exception as e:
                warn(f"Please try again. {e}")   
        log("Setting up...")
        coros = [scrapeGroupUsernames(loc, groupId)]
        log("Finished setup...")

        log("Running...")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(conGather(*coros))
        log("Finished!")
        log(f"You can find scraped usernames in '{loc}'.")
        pause()

def statusChanger(cookies, proxies):
    setTitle("Aurora II | Status Changer")
    setup()

    while True:
        try:
            status = inp("Status (leave blank for default)")
            if status == "":
                status = "Aurora > Versatile"
            break
        except Exception as e:
            warn(f"Please try again. {e}")

    log("Setting up...")
    coros = [c.changeStatus(random.choice(proxies), status) for c in cookies]
    log("Finished setup...")

    log("Running...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(conGather(*coros))

    log("Finished!")
    pause()

def credits():
    setup()
    setTitle("Aurora II | Credits")
    log("Dev: Funny Lasagna Cat#1200 | bc1qw5p2h8xnr0skh2nq8s8stjj22c3rmqxv0qpyaj")
    log("Dev: Klem#0777 | bc1q53865z05lw9j8gas7wwcf46gcm825uhum6pxe7")
    log("Dev: LabGuy94#0001")
    log("Owner: Velix#6790")
    log("Retired Owner: novuh#2719")
    pause()
