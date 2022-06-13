import zipfile
import requests
import io
from src.frontend import *
from src.endpoints import auth, get_hwid

clear()
setTitle("Aurora II Updater")

log("Checking your authorization...")

with open('license.txt','r') as f:
    try:
        authentication = auth(f.readlines()[0])
    except:
        authentication = auth(inp('Enter license: '), False)
try:
    if authentication['bool'] == False:
        fatal("You are not authorized to use this software.")
        fatal(f"- > {authentication['answer']}")
        log("You can buy a license @ auroratools.shop")
        close()
except:
    pass

ok("You are authorized to use this program.")

##
log("Downloading the latest version of Aurora...")
try:
    data = requests.get("https://api.auroratools.shop/aurora.zip")
except Exception as e:
    fatal("There was a problem downloading Aurora!")
    hint(e)
    log("Please report this in the Discord.")
    close()

ok("Successfully downloaded the latest version of Aurora!")
try:
    z = zipfile.ZipFile(io.BytesIO(data.content))
    log("Extracting...")
    z.extractall("Aurora")
    z.close()
except Exception as e:
    fatal("There was a problem extracting Aurora contents!")
    hint(e)
    log("Please report this in the Discord.")
    close()

ok("Aurora has been sucessfully installed.")
log("You can view it in the Aurora folder that appeared in the current")
log("directory.")
close()