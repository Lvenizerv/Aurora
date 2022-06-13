# A2A14B1D-1AF3-C791-9BBC-EE33CC7A0A6F

from tkinter import N
import aiohttp
from asyncio import sleep
import requests

from src import frontend

async def solve2Captcha(apikey, pageurl, blob, type="signup"):
    pkey = ""
    if type == "signup":
        pkey = "A2A14B1D-1AF3-C791-9BBC-EE33CC7A0A6F"
    else:
        pkey = "63E4117F-E727-42B4-6DAA-C8448E9B137F"
    async with aiohttp.ClientSession(trust_env=False) as session:
        async with session.post(f"http://2captcha.com/in.php?key={apikey}&method=funcaptcha&publickey={pkey}&surl=https://roblox-api.arkoselabs.com&pageurl={pageurl}&soft_id=3190&data[blob]={blob}") as res:
            response = await res.text()
            if "OK" in response:
                id = response.replace("OK|", "")
            elif "ERROR_WRONG_USER_KEY" in response:
                frontend.warn("2Captcha returned 'ERROR_WRONG_USER_KEY', is your 2captcha key correct?")
                await session.close()
                return None
            elif 'ERROR_KEY_DOES_NOT_EXIST' in response:
                frontend.warn("It seems the 2captcha key you provided does not exist.")
                await session.close()
                return None
            elif 'ERROR_ZERO_BALANCE' in response:
                frontend.warn("You have no balance in your 2captcha account.")
                await session.close()
                return None
            elif 'ERROR_NO_SLOT_AVAILABLE' in response:
                frontend.warn("2captcha solving queue too long.")
                await session.close()
                return None
            else:
                frontend.warn(f"2captcha returned '{response}'.")
                await session.close()
                return None

            await sleep(15)

            while True:
                await sleep(5)
                async with session.get(f"http://2captcha.com/res.php?key={apikey}&action=get&id={id}") as res:
                    response = await res.text()
                    if 'CAPCHA_NOT_READY' in response:
                        continue
                    elif 'ERROR_CAPTCHA_UNSOLVABLE' in response:
                        frontend.warn("Captcha unsolvable, you have not been charged.")
                        await session.close()
                        return None
                    elif '|' in response:
                        requests.get(f"http://2captcha.com/res.php?key={apikey}&action=reportbad&id={id}")
                        await session.close()
                        return response
                    else:
                        frontend.warn(f"2captcha returned '{response}'.")
                        await session.close()
                        return None

async def solveAntiCaptcha(apikey, pageurl, blob, timeout, pkey="signup"):
    pkey = ""
    if type == "signup":
        pkey = "A2A14B1D-1AF3-C791-9BBC-EE33CC7A0A6F"
    else:
        pkey = "63E4117F-E727-42B4-6DAA-C8448E9B137F"
    async with aiohttp.ClientSession(trust_env=False) as session:

        j = {
            "clientKey": apikey,
            "softId": "1008",
            "task": {
                "type": "FunCaptchaTaskProxyless",
                "websiteURL": pageurl,
                "funcaptchaApiJSSubdomain": "roblox-api.arkoselabs.com",
                "data": "{\"blob\":\"%s\"}" % blob,
                "websitePublicKey": pkey
            }
        }

        async with session.post("https://api.anti-captcha.com/createTask", json=j) as res:
            content = await res.json()
            if "errorCode" in content:
                if content["errorCode"] == "ERROR_KEY_DOES_NOT_EXIST":
                    frontend.fatal("It seems the anticaptcha key you provided does not exist.")
                    await session.close()

                elif content["errorCode"] == "ERROR_NO_SLOT_AVAILABLE":
                    frontend.fatal("anticaptcha solving queue too busy.")
                    await session.close()

                elif content["errorCode"] == "ERROR_ZERO_BALANCE":
                    frontend.fatal("You have no balance in your anticaptcha account.")
                    await session.close()

                elif content["errorCode"] == "ERROR_CAPTCHA_UNSOLVABLE":
                    frontend.warn("Captcha is unsolvable. (charged due to AntiCaptcha policy)")
                    await session.close()

                else:
                    frontend.fatal(f"AntiCaptcha returned '{content['errorCode']}'.")
                    await session.close()
                return None

            else:
                task = content['taskId']
        
        tries = 0
        while True:
            await sleep(5)
            async with session.post("https://api.anti-captcha.com/getTaskResult", json={"clientKey": apikey, "taskId": task}) as res:
                content = await res.json()

                if "errorCode" in content:
                    if content["errorCode"] == "ERROR_KEY_DOES_NOT_EXIST":
                        frontend.fatal("It seems the anticaptcha key you provided does not exist.")
                        await session.close()
                    elif content["errorCode"] == "ERROR_NO_SLOT_AVAILABLE":
                        frontend.fatal("anticaptcha solving queue too busy.")
                        await session.close()
                    elif content["errorCode"] == "ERROR_ZERO_BALANCE":
                        frontend.fatal("You have no balance in your anticaptcha account.")
                        await session.close()
                    elif content["errorCode"] == "ERROR_CAPTCHA_UNSOLVABLE":
                        frontend.warn("Captcha is unsolvable. (charged due to AntiCaptcha policy)")
                        await session.close()
                    else:
                        frontend.fatal(f"AntiCaptcha returned '{content['errorCode']}'.")
                        await session.close()
                    return None

                elif "solution" in content:
                    await session.close()
                    return content["solution"]["token"]
                elif tries >= timeout:
                    await session.close()
                    frontend.warn(f"Max retries ({timeout}, ~{5*timeout}s) was exceeded (anticaptcha).")
                    return 
                else:
                    tries += 1
