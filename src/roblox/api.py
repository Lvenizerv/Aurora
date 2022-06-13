import asyncio
from . import botting

async def conGather(*tasks):
    sem = asyncio.Semaphore(500)

    async def semTask(task):
        async with sem:
            return await task
    return await asyncio.gather(*(semTask(task) for task in tasks))

def setWindowsPolicy():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)

def checkAll(cookies: list[botting.Cookie]):
    loop = asyncio.get_event_loop()
    coros = [ck.check() for ck in cookies]
    valids = loop.run_until_complete(conGather(*coros))
    return list(filter(None, valids))
