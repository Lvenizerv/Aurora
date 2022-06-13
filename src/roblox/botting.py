import re
import time
import aiohttp
import asyncio
from src import frontend
from bs4 import BeautifulSoup
import json as json_
from . import solving
from rstr import xeger
from mailtm import Email
from time import sleep
import requests
import subprocess
import random
# OOP approach
# Goals:
# - minimal interface
# - as less operators/logic statements as possible
# - minimize method/func usage to reduce GIL lookup
# - comprehensive comments
# - make code look messy

async def proxyCheck(location, proxy):
    async with aiohttp.ClientSession(trust_env=False) as session:
        try:
            async with session.get("https://roblox.com", proxy = f"http://{proxy}", timeout=10) as res:
                if res.status == 200 and res.json()["origin"] == proxy:
                    frontend.ok("Proxy is valid")
                    with open(location, "a") as f:
                        f.write(proxy + "\n")
                    await session.close()

        except aiohttp.ClientConnectorError:
            frontend.fatal("Proxy is invalid")
            await session.close()

        except aiohttp.ClientHttpProxyError:
            frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
            await session.close()

        except Exception as e:
            frontend.fatal(f"(PC) An unexpected error has occured! '{e}'")
            await session.close()

async def checkGroup(groupId, proxy, cookie=None):
    try:
        async with aiohttp.ClientSession(trust_env=False) as session:
            async with session.get(f"https://groups.roblox.com/v1/groups/{groupId}", proxy = f"http://{proxy}") as res:
                j = await res.json()
                if j["owner"] == None:
                    if "isLocked" in j:
                        frontend.log(f"Group '{groupId}' is locked.")
                    elif j["publicEntryAllowed"] == False:
                        frontend.log(f"Group '{groupId}' does not allow public entry.")
                    else:
                        frontend.ok(f"https://www.roblox.com/groups/{groupId}/")
    except aiohttp.ClientConnectorError:
        frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
        await session.close()

    except aiohttp.ClientHttpProxyError:
        frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
        await session.close()

    except Exception as e:
        frontend.warn(f"(CG) An exception occured '{e}', please report this if the issue persists.")
        await session.close()

async def getAssetInformation(assetId: int):
    async with aiohttp.ClientSession(trust_env=False) as session:
        async with session.get(f"https://api.roblox.com/Marketplace/ProductInfo?assetId={assetId}") as res:
            json = await res.json()
    await session.close()
    return json

async def allyRequest(cookie, groupId, toAlly):
    pass

async def downloadShirt(assetId, proxy):
    async with aiohttp.ClientSession(trust_env=False) as session:
        async with session.get(f"https://api.roblox.com/Marketplace/ProductInfo?assetId={assetId}") as res:
            try:
                content = await res.json()
                name = content['Name']
            except:
                frontend.warn(f"Shirt '{assetId}' does not exist.")
                return None
            if content["AssetTypeId"] == 11:
                with open(f'shirts/{name}.png', 'wb') as f:
                    try:
                        async with session.get(f'https://assetdelivery.roblox.com/v1/asset?id={assetId}') as res:
                            data = await res.text()
                            x = re.findall(r'<url>(.+ ?)(?=</url>)', data)[0].replace("http://www.roblox.com/asset/?id=", "")
                            async with session.get("https://assetdelivery.roblox.com/v1/asset?id=" + str(x)) as res:
                                dat = await res.content.read()
                                f.write(dat)
                                frontend.ok(f"Sucessfully downloaded '{name}'!")
                    except:
                            frontend.warn(f"There was a problem fetching required data for '{assetId}'.")
                            return None
            else: 
                frontend.warn(f"Shirt '{assetId}' is not a shirt.")
                return None

async def generateCookie(location, username, password, captchaType, captchaKey, timeout, proxy):
    sendData = {
        "username": username,
        "password": password,
        "birthday": "18 Oct 2000", 
        "gender": 2,
        "isTosAgreementBoxChecked": True,
        "context": "MultiverseSignupForm",
        "referralData": None,
        "displayAvatarV2": False,
        "displayContextV2": False
    }

    async with aiohttp.ClientSession(trust_env=False) as session:
        try:
            async with session.post("https://auth.roblox.com/v2/login", proxy = f"http://{proxy}", json={"ctype": "Username", "cvalue": "an0nym0us_n0b0dy", "password": "notmyrealpasswordlmao"}) as res:
                token = res.headers['x-csrf-token']

            async with session.post("https://auth.roblox.com/v2/signup", json=sendData, headers={"x-csrf-token": token}, proxy = f"http://{proxy}") as res:
                json = await res.json()
                captchaId, blob = json['errors'][0]['fieldData'].split(",")
                sendData.update({"captchaId": captchaId})
                sendData.update({"captchaProvider": "PROVIDER_ARKOSE_LABS"})
            
            if captchaType == '2captcha':
                ctoken = await solving.solve2Captcha(captchaKey, "https://www.roblox.com/account/signupredir", blob)
                if ctoken == None:
                    await session.close()
                    return None
                else:
                    sendData.update({"captchaToken": ctoken})

            elif captchaType == 'anticaptcha':
                ctoken = await solving.solveAntiCaptcha(captchaKey, "https://www.roblox.com", blob, timeout)
                if ctoken == None:
                    await session.close()
                    return None
                else:
                    sendData.update({"captchaToken": ctoken})
            

            async with session.post("https://auth.roblox.com/v2/signup", json=sendData, headers={"x-csrf-token": token}, proxy = f"http://{proxy}") as res:
                if res.status == 200:
                    frontend.ok(f"Successfully generated a cookie! ('{username}')")
                    await session.close()
                    value = str(res.cookies['.ROBLOSECURITY']).split(";")[0].replace("Set-Cookie: .ROBLOSECURITY=", "")
                    open(location, 'a').write(value + "\n")
                else:
                    j = await res.json()
                    frontend.warn(f"Could not generate a cookie. '{j['errors'][0]['message']}' ('{username}')")
                    await session.close()
                    return None

        except aiohttp.ClientConnectorError:
            frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
            await session.close()

        except aiohttp.ClientHttpProxyError:
            frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
            await session.close()

        except Exception as e:
            frontend.fatal(f"(CG) An unexpected error has occured! '{e}'")
            await session.close()

async def scrapeShirts(location, proxy, cursor):
        async with aiohttp.ClientSession(trust_env=False) as session:
            try:
                async with session.get(f"https://catalog.roblox.com/v1/search/items?category=Clothing&cursor={cursor}&limit=60&subcategory=ClassicShirts", proxy=f"http://{proxy}") as res:
                    if res.status == 200:
                        for audio in res.json()["data"]:
                            with open(location, "a") as f:
                                f.write(audio["id"] + "\n")
                                frontend.ok("Scraped a shirt!")
                        if res.json()["nextCursor"] != None:
                            return res.json()["nextCursor"]
                        else:
                            return None
                    else:
                        frontend.warn("Failed to get front page shirts.")
                                
            except aiohttp.ClientConnectorError:
                frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
                await session.close()

            except aiohttp.ClientHttpProxyError:
                frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
                await session.close()

            except Exception as e:
                frontend.fatal(f"(CG) An unexpected error has occured! '{e}'")
                await session.close()

async def scrapeGroupUsernames(location, groupId):
    try:
        async with aiohttp.ClientSession(trust_env=False) as session:
            cursor = ""
            usernames = []
            while True:

                if cursor == None:
                    break

                async with session.get(f'https://groups.roblox.com/v1/groups/{groupId}/users?cursor={cursor}') as r:

                    json = await r.json()

                    for user in json['data']:
                        with open(location, "a") as f:
                            username = user['user']['username']
                            f.write(username + "\n")
                            usernames.append(username)
                            frontend.ok(f'Scraped username ({username})')

                    cursor = json['nextPageCursor']

            frontend.log(f'Successfully scraped {len(usernames)} usernames from group {groupId}!')
                        
    except aiohttp.ClientConnectorError:
        frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
        await session.close()

    except aiohttp.ClientHttpProxyError:
        frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
        await session.close()

    except Exception as e:
        frontend.fatal(f"(GUS) An unexpected error has occured! '{e}'")
        await session.close()

class Cookie:
    def __init__(self, cookie: str):
        """ROBLOX bot account."""
        self.cookie = {".ROBLOSECURITY": cookie}
        self.auth = ""
        self.userAgent = ""

    async def setAuth(self, proxy: str=None):
        """Gets the X-CSRF-TOKEN"""

        # 0: set up HTTP session
        try:
            async with aiohttp.ClientSession(cookies=self.cookie) as session:
                # 1: make the request I need
                if proxy != None:
                    async with session.post("https://auth.roblox.com/v2/login", proxy = f"http://{proxy}", headers = {"user-Agent": self.userAgent}) as res:
                        # 2: work with response content
                        self.auth = res.headers['x-csrf-token']
                else:
                    async with session.post("https://auth.roblox.com/v2/login", headers = {"user-Agent": self.userAgent}) as res:
                        # 2: work with response content
                        self.auth = res.headers['x-csrf-token']
            await session.close()
            return self.auth
        except aiohttp.ClientConnectorError:
            frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
            await session.close()

        except aiohttp.ClientHttpProxyError:
            frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
            await session.close()

        except Exception as e:
            frontend.fatal(f"(csrf) An unexpected error has occured! '{e}'")
            await session.close()
            
    async def check(self):
        """Checks the cookie, returns value on success."""
        async with aiohttp.ClientSession(cookies=self.cookie) as session:
            async with session.get("https://users.roblox.com/v1/users/authenticated", headers = {"user-Agent": self.userAgent}) as res:
                try:
                    data = await res.json()
                    frontend.ok(f"Cookie is valid! ['{data['name']}', '{data['id']}']")
                    await session.close()
                    return self.cookie['.ROBLOSECURITY']
                except KeyError:
                    frontend.warn("Cookie is invalid.")
                    await session.close()
                    return None
                except aiohttp.ContentTypeError:
                    frontend.hint(res.status)
                    frontend.warn("Cookie is invalid.")
                    await session.close()
                    return None
                except Exception as e:
                    frontend.warn(f"(CC) Unexpected exception occured: {e}")
                    await session.close()
                    return None
    
    async def botAsset(self, proxy: str, assetId: int, productId: int, creatorId: int):
        """Buys, then sells asset"""
        try:
            if self.auth == "":
                await self.setAuth(proxy)
                
            async with aiohttp.ClientSession(cookies=self.cookie) as session:
                async with session.post(f"https://economy.roblox.com/v1/purchases/products/{productId}", headers = {'x-csrf-token': self.auth, "User-Agent": self.userAgent}, json = {"expectedCurrency": 1,"expectedPrice": 0,"expectedSellerId": creatorId}, proxy = f"http://{proxy}") as res:
                    if res.status == 200:
                        async with session.post("https://www.roblox.com/asset/delete-from-inventory", headers = {'x-csrf-token': self.auth, "User-Agent": self.userAgent}, json = {"assetId": assetId}, proxy = f"http://{proxy}") as res:
                            if res.status == 200:
                                frontend.ok(f"Bought & Deleted Asset [{assetId}]")
                            else:
                                frontend.warn(f"({res.status}) Could not DELETE asset [{assetId}]")
                    else:
                        frontend.warn(f"({res.status}) Could not BUY asset [{assetId}]")
                await session.close()

        except aiohttp.ClientConnectorError:
            frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
            await session.close()

        except aiohttp.ClientHttpProxyError:
            frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
            await session.close()

        except Exception as e:
            frontend.warn(f"(MB) An exception occured '{e}', please report this if the issue persists.")
            await session.close()

    async def favorite(self, proxy: str, assetId: int):
        """Toggles a favorite"""
        try:
            if self.auth == "":
                await self.setAuth(proxy)
            
            async with aiohttp.ClientSession(cookies=self.cookie) as session:
                async with session.post(f"https://www.roblox.com/v2/favorite/toggle", headers = {'x-csrf-token': self.auth, "User-Agent": self.userAgent}, json = {"itemTargetId": assetId, "favoriteType": "Asset"}, proxy = f"http://{proxy}") as res:
                    if res.status == 200:
                        frontend.ok(f"Successfully sent a favorite toggle! [{assetId}]")
                    else:
                        frontend.warn(f"({res.status}) Could not sent a favorite toggle. [{assetId}]")

        except aiohttp.ClientConnectorError:
            frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
            await session.close()

        except aiohttp.ClientHttpProxyError:
            frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
            await session.close()

        except Exception as e:
            frontend.warn(f"(FB) An exception occured '{e}', please report this if the issue persists.")
            await session.close()

    async def friend(self, userId: int):
        try:
            if self.auth == "":
                await self.setAuth()
            
            async with aiohttp.ClientSession(cookies=self.cookie) as session:
                async with session.post(f"https://friends.roblox.com/v1/users/{userId}/request-friendship", headers = {'x-csrf-token': self.auth, "User-Agent": self.userAgent}) as res:
                    if res.status == 200:
                        frontend.ok(f"Successfully sent a friend request to your target!")
                    else:
                        frontend.warn(f"({res.status}) Could not send a friend request.")

        except aiohttp.ClientConnectorError:
            frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
            await session.close()

        except aiohttp.ClientHttpProxyError:
            frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
            await session.close()

        except Exception as e:
            frontend.warn(f"(FR) An exception occured '{e}', please report this if the issue persists.")
            await session.close()

    async def allyRequest(self, group, toAlly, proxy):
        if self.auth == "":
            await self.auth()
        
        async with aiohttp.ClientSession(cookies=self.cookie) as session:
            async with session.post(f'https://groups.roblox.com/v1/groups/{group}/relationships/allies/{toAlly}', headers = {'x-csrf-token': self.auth, "User-Agent": self.userAgent}, proxy = f"http://{proxy}"):
                pass

    async def claimGroup(self, groupId, proxy):
        pass

    async def follow(self, userId: int, captchaType, captchaKey, timeout, proxy):
        """Follows a user"""
        sendData = {
            "captchaId": "string",
            "captchaToken": "string",
            "captchaProvider": "string"
        }

        #63E4117F-E727-42B4-6DAA-C8448E9B137F

        async with aiohttp.ClientSession(trust_env=False) as session:
            try:
                async with session.post("https://auth.roblox.com/v2/login", proxy = f"http://{proxy}", json={"ctype": "Username", "cvalue": "an0nym0us_n0b0dy", "password": "notmyrealpasswordlmao"}) as res:
                    token = res.headers['x-csrf-token']

                async with session.post(f"https://friends.roblox.com/v1/users/{userId}/follow", json=sendData, headers={"x-csrf-token": token}, proxy = f"http://{proxy}") as res:
                    json = await res.json()
                    captchaId = json_.loads(json['errors'][0]['fieldData'])["unifiedCaptchaId"]
                    blob = json_.loads(json['errors'][0]['fieldData'])["dxBlob"]
                    sendData.update({"captchaId": captchaId})
                    sendData.update({"captchaProvider": "PROVIDER_ARKOSE_LABS"})
                
                if captchaType == '2captcha':
                    ctoken = await solving.solve2Captcha(captchaKey, "https://www.roblox.com/account/signupredir", blob, "follow")
                    if ctoken == None:
                        await session.close()
                        return None
                    else:
                        sendData.update({"captchaToken": ctoken})

                elif captchaType == 'anticaptcha':
                    ctoken = await solving.solveAntiCaptcha(captchaKey, "https://www.roblox.com", blob, timeout, "follow")
                    if ctoken == None:
                        await session.close()
                        return None
                    else:
                        sendData.update({"captchaToken": ctoken})
                
                async with session.post(f"https://friends.roblox.com/v1/users/{userId}/follow", json=sendData, headers={"x-csrf-token": token}, proxy = f"http://{proxy}") as res:
                    if res.status == 200:
                        frontend.ok(f"Successfully followed user [{userId}]")
                        await session.close()
                    else:
                        j = await res.json()
                        frontend.warn(f"Could not follow user. '{j['errors'][0]['message']}' [{userId}]")
                        await session.close()
                        return None

            except aiohttp.ClientConnectorError:
                frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
                await session.close()

            except aiohttp.ClientHttpProxyError:
                frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
                await session.close()

            except Exception as e:
                frontend.fatal(f"(FB) An unexpected error has occured! '{e}'")
                await session.close()

    async def loginUP(self, location, captchaType, captchaKey, timeout, proxy):
        print(self.cookie)
        username = self.cookie[".ROBLOSECURITY"].split(":")[0]
        password = self.cookie[".ROBLOSECURITY"].split(":")[1]

        sendData = {"ctype": "Username", "cvalue": username, "password": password}

        async with aiohttp.ClientSession(trust_env=False) as session:
            try:
                async with session.post("https://auth.roblox.com/v2/login", proxy = f"http://{proxy}", json=sendData) as res:
                    token = res.headers['x-csrf-token']

                async with session.post("https://auth.roblox.com/v2/login", json=sendData, headers={"x-csrf-token": token}, proxy = f"http://{proxy}") as res:
                    json = await res.json()
                    captchaId, blob = json['errors'][0]['fieldData'].split(",")
                    sendData.update({"captchaId": captchaId})
                    sendData.update({"captchaProvider": "PROVIDER_ARKOSE_LABS"})
                
                if captchaType == '2captcha':
                    ctoken = await solving.solve2Captcha(captchaKey, "https://www.roblox.com/account/signupredir", blob, "login")
                    if ctoken == None:
                        await session.close()
                        return None
                    else:
                        sendData.update({"captchaToken": ctoken})

                elif captchaType == 'anticaptcha':
                    ctoken = await solving.solveAntiCaptcha(captchaKey, "https://www.roblox.com", blob, timeout, "login")
                    if ctoken == None:
                        await session.close()
                        return None
                    else:
                        sendData.update({"captchaToken": ctoken})
                

                async with session.post("https://auth.roblox.com/v2/login", json=sendData, headers={"x-csrf-token": token}, proxy = f"http://{proxy}") as res:
                    if res.status == 200:
                        frontend.ok(f"Successfully generated a cookie from username and password! ('{username}')")
                        await session.close()
                        value = str(res.cookies['.ROBLOSECURITY']).split(";")[0].replace("Set-Cookie: .ROBLOSECURITY=", "")
                        open(location, 'a').write(value + "\n")
                    else:
                        j = await res.json()
                        frontend.warn(f"Could not generate a cookie from username and password. '{j['errors'][0]['message']}' ('{username}')")
                        await session.close()
                        return None

            except aiohttp.ClientConnectorError:
                frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
                await session.close()

            except aiohttp.ClientHttpProxyError:
                frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
                await session.close()

            except Exception as e:
                frontend.fatal(f"(C2C) An unexpected error has occured! '{e}'")
                await session.close()

    async def upc2Cookie(self, location):
        try:
            newcookie = f"{self.cookie.split(':')[2]}:{self.cookie.split(':')[3]}"
            with open(location, "a") as f:
                f.write(newcookie + "\n")
                frontend.ok(f"Successfully converted cookie")
        except:
            frontend.warn("Cookie not in U:P:C format")

    async def verify(self, location, proxy: str):
        """Email verifies a cookie"""
        try:
            if self.auth == "":
                await self.setAuth()
            async with aiohttp.ClientSession(cookies=self.cookie) as session:
                email = ''.join(random.choice("abcdefghijklmnopqrstuvwxyz") for x in range(10))
                async with session.post("https://accountsettings.roblox.com/v1/email", json={"emailAddress": email + "@vddaz.com", "password": ""}, proxy="http://" + proxy, headers={"X-CSRF-TOKEN": self.auth}) as res:
                    if res.status != 200:
                        if res.json()["errors"][0]["code"] == 8:
                            frontend.warn("Account already has email")
                        if res.json()["errors"][0]["code"] == 6:
                            frontend.warn("Too many attempts")
                    else:
                        time.sleep(10)
                        id = await session.get(f"https://www.1secmail.com/api/v1/?action=getMessages&login={email}&domain=vddaz.com").json()[0]["id"]
                        body = await session.get(f"https://www.1secmail.com/api/v1/?action=readMessage&login={email}&domain=vddaz.com&id={id}").json()["body"]
                        S = BeautifulSoup(body, 'lxml')
                        emailbutton = S.find_all(class_="email-button")[0]
                        emailurl = emailbutton.get("href")
                        async with session.post("https://accountinformation.roblox.com/v1/email/verify", proxy="http://" + proxy, json={"ticket": emailurl.split("=")[1]}, headers={"X-CSRF-TOKEN": self.auth}) as res:
                            if res.status == 200:
                                frontend.ok("Successfully verified email")
                            else:
                                frontend.warn("Could not verify email")
                    
        except aiohttp.ClientConnectorError:
            frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
            await session.close()

        except aiohttp.ClientHttpProxyError:
            frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
            await session.close()

        except Exception as e:
            frontend.warn(f"(EV) An exception occured '{e}', please report this if the issue persists.")
            await session.close()

    async def refreshCookie(self, location, proxy):
            try:
                if self.auth == "":
                    await self.setAuth()

                async with aiohttp.ClientSession(cookies=self.cookie) as session:
                    async with session.post("https://www.roblox.com/authentication/signoutfromallsessionsandreauthenticate", proxy = f"http://{proxy}", headers={'x-csrf-token': self.auth}) as res:
                        if res.status == 200:
                            newcookie = str(res.cookies['.ROBLOSECURITY']).split(";")[0].replace("Set-Cookie: .ROBLOSECURITY=", "")
                            frontend.ok("Successfully refreshed cookie")
                            with open(location, "a") as f:
                                f.write(newcookie + "\n")
                            await session.close()
                        elif res.status == 403:
                            frontend.warn("Cookie is invalid!")
                            await session.close()
                        else:
                            frontend.warn(f"Could not refresh cookie. ({res.status})")
                            await session.close()

            except aiohttp.ClientConnectorError:
                frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
                await session.close()
            
            except aiohttp.ClientHttpProxyError:
                frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
                await session.close()
            
            except Exception as e:
                frontend.warn(f"(CR) An exception occured '{e}', please report this if the issue persists.")
                await session.close()
    
    async def changeDisplay(self, name, proxy):
            try:
                if self.auth == "":
                    await self.setAuth()

                async with aiohttp.ClientSession(cookies=self.cookie) as session:
                    userId = session.get("https://users.roblox.com/v1/users/authenticated", headers={'x-csrf-token': self.auth}, proxies={"http": f"http://{proxy}"}).json()["id"]
                    async with session.post(f"https://users.roblox.com/v1/users/{userId}/display-names", proxy = f"http://{proxy}", headers={'x-csrf-token': self.auth}, data={"newDisplayName":name}) as res:
                        if res.status == 200:
                            frontend.ok(f"Successfully changed display name for {userId}")
                            await session.close()
                        elif res.status == 403:
                            frontend.warn("Cookie is invalid!")
                            await session.close()
                        else:
                            frontend.warn(f"Could not change display name. ({res.status})")
                            await session.close()

            except aiohttp.ClientConnectorError:
                frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
                await session.close()
            
            except aiohttp.ClientHttpProxyError:
                frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
                await session.close()
            
            except Exception as e:
                frontend.warn(f"(DC) An exception occured '{e}', please report this if the issue persists.")
                await session.close()

    async def visitGame(self, gameId):
            try:
                if self.auth == "":
                    await self.setAuth()

                async with aiohttp.ClientSession(cookies=self.cookie) as session:
                    authTicketreq = await session.post('https://auth.roblox.com/v1/authentication-ticket/', headers={'referer':f'https://www.roblox.com/games/{gameId}', 'x-csrf-token':self.auth})
                    authTicket = authTicketreq.headers["rbx-authentication-ticket"]
                    browserId = random.randint(1000000, 10000000)
                    game = subprocess.Popen(f"start roblox-player:1+launchmode:play+gameinfo:{authTicket}+launchtime:{browserId}+placelauncherurl:https%3A%2F%2Fassetgame.roblox.com%2Fgame%2FPlaceLauncher.ashx%3Frequest%3DRequestGame%26browserTrackerId%3D{browserId}%26placeId%3D{gameId}%26isPlayTogetherGame%3Dfalse+browsertrackerid:{browserId}+robloxLocale:en_us+gameLocale:en_us+channel:", shell=True)
                    sleep(5)
                    subprocess.Popen(f"TASKKILL /F /PID {game.pid} /T")

            except aiohttp.ClientConnectorError:
                frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
                await session.close()
            
            except aiohttp.ClientHttpProxyError:
                frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
                await session.close()
            
            except Exception as e:
                frontend.warn(f"(VB) An exception occured '{e}', please report this if the issue persists.")
                await session.close()

    async def rateGame(self, gameId, rating):
            try:
                if self.auth == "":
                    await self.setAuth()

                async with aiohttp.ClientSession(cookies=self.cookie) as session:
                    authTicketreq = await session.post('https://auth.roblox.com/v1/authentication-ticket/', headers={'referer':f'https://www.roblox.com/games/{gameId}', 'x-csrf-token':self.auth})
                    authTicket = authTicketreq.headers["rbx-authentication-ticket"]
                    browserId = random.randint(1000000, 10000000)
                    game = subprocess.Popen(f"start roblox-player:1+launchmode:play+gameinfo:{authTicket}+launchtime:{browserId}+placelauncherurl:https%3A%2F%2Fassetgame.roblox.com%2Fgame%2FPlaceLauncher.ashx%3Frequest%3DRequestGame%26browserTrackerId%3D{browserId}%26placeId%3D{gameId}%26isPlayTogetherGame%3Dfalse+browsertrackerid:{browserId}+robloxLocale:en_us+gameLocale:en_us+channel:", shell=True)
                    sleep(5)
                    subprocess.Popen(f"TASKKILL /F /PID {game.pid} /T")
                    async with session.post(f"https://www.roblox.com/voting/vote?assetId={gameId}&vote={rating}", headers={'x-csrf-token': self.auth}) as res:
                        if res.status == 200:
                            if rating == True:
                                frontend.ok("Successfully liked game!")
                            else:
                                frontend.ok("Successfully disliked game!")
                            await session.close()
                        elif res.status == 403:
                            frontend.warn("Cookie is invalid!")
                            await session.close()
                        else:
                            frontend.warn(f"Could not rate game. ({res.status})")
                            await session.close()

            except aiohttp.ClientConnectorError:
                frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
                await session.close()
            
            except aiohttp.ClientHttpProxyError:
                frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
                await session.close()
            
            except Exception as e:
                frontend.warn(f"(LB) An exception occured '{e}', please report this if the issue persists.")
                await session.close()
    
    async def reportUser(self, userId):
            try:
                if self.auth == "":
                    await self.setAuth()

                async with aiohttp.ClientSession(cookies=self.cookie) as session:
                    __RequestVerificationToken = session.get(f'https://www.roblox.com/abusereport/userprofile?id={userId}').text.split('<input name="__RequestVerificationToken" type="hidden" value="')[1].split('" />')[0]
                    async with session.post(f'https://www.roblox.com/abusereport/userprofile?id={userId}', headers={'x-csrf-token': self.auth, '__RequestVerificationToken': __RequestVerificationToken}) as res:
                        frontend.ok("Successfully reported user!")

            except aiohttp.ClientConnectorError:
                frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
                await session.close()
            
            except aiohttp.ClientHttpProxyError:
                frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
                await session.close()
            
            except Exception as e:
                frontend.warn(f"(RB) An exception occured '{e}', please report this if the issue persists.")
                await session.close()
    
    async def regionChange(self, location, proxy):
         async with aiohttp.ClientSession(trust_env=False) as session:
            try:
                if self.auth == "":
                    await self.setAuth(proxy=proxy)
                authticket = ""
                async with session.post("https://auth.roblox.com/v1/authentication-ticket/", headers={"Origin": "https://www.roblox.com", "Referer": "https://www.roblox.com/","X-CSRF-TOKEN": self.auth, "User-Agent": "Roblox/WinInet"}, json={}, proxy = f"http://{proxy}", cookies=self.cookie) as res:
                    if res.status == 200:
                        if not res.headers["rbx-authentication-ticket"] == None:
                            authticket = res.headers["rbx-authentication-ticket"]
                    else:
                        frontend.warn("Failed to swap region due to error 1")
                        return None
                async with session.post("https://auth.roblox.com/v1/authentication-ticket/redeem", headers={"Accept": "*/*","Connection": "keep-alive","Cache-Control": "no-cache","Requester": "Client","PlayerCount": "0","RBXAuthenticationNegotiation": "https://www.roblox.com/","User-Agent": "Roblox/WinInet"}, proxy=f"http://{proxy}", json={"authenticationTicket": authticket}, cookies=None) as res:
                    if res.status == 200:
                        with open(location, "a") as f:
                            f.write(str(res.cookies['.ROBLOSECURITY']).split(";")[0].replace("Set-Cookie: .ROBLOSECURITY=", "") + "\n")
                            frontend.ok("Successfully swapped region")
                            return None
                    else:
                        frontend.warn("Failed to swap region due to error 2")
                        return None
            except aiohttp.ClientConnectorError:
                frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
                await session.close()

            except aiohttp.ClientHttpProxyError:
                frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
                await session.close()

            except Exception as e:
                frontend.fatal(f"(RC) An unexpected error has occured! '{e}'")
                await session.close()

    async def kill(self, proxy):
        async with aiohttp.ClientSession(cookies=self.cookie, trust_env=False) as session:
            try:
                if self.auth == "":
                    await self.setAuth(proxy=proxy)
                async with session.get("https://auth.roblox.com/v2/logout", headers={"X-CSRF-TOKEN": self.auth}, proxy=f"http://{proxy}") as res:
                    if res.status == 200:
                        frontend.ok("Successfully killed cookie")
                        return None
                    else:
                        frontend.warn(f"Failed to kill cookie. ({res.status})")
                        return None
            except aiohttp.ClientConnectorError:
                frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
                await session.close()

            except aiohttp.ClientHttpProxyError:
                frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
                await session.close()

            except Exception as e:
                frontend.fatal(f"(CK) An unexpected error has occured! '{e}'")
                await session.close()

    async def changeStatus(self, proxy, status):
        async with aiohttp.ClientSession(cookies=self.cookie, trust_env=False) as session:
            try:
                if self.auth == "":
                    await self.setAuth(proxy=proxy)

                async with session.post("https://accountinformation.roblox.com/v1/description", headers={"X-CSRF-TOKEN": self.auth, 'Content-Type': 'application/json'}, json={"description": status}, proxy=f"http://{proxy}") as res:
                    if res.status == 200:
                        frontend.ok("Successfully changed status")
                        return None
                    else:
                        frontend.warn(f"Failed to change status. ({res.status})")
                        return None
            except aiohttp.ClientConnectorError as e:
                frontend.fatal(e)
                frontend.fatal("Oh no! There was a proxy issue. Please check documentation.")
                await session.close()

            except aiohttp.ClientHttpProxyError:
                frontend.fatal("Oh no! There was a proxy error. Please ensure you have proper proxy authentication!")
                await session.close()

            except Exception as e:
                frontend.fatal(f"(SC) An unexpected error has occured! '{e}'")
                await session.close()