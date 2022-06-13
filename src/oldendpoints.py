import requests
import subprocess

def redeem(key: str, hwid: str) -> bool:
    """redeems a key"""
    p = {
        "key": key,
        "hwid": hwid
    }
    r = requests.post("https://api.novuh.dev/aurtemp/redeem", params=p)
    if r.status_code == 200:
        return True
    elif r.status_code == 403:
        return False
    else:
        return False

def auth(hwid: str) -> bool:
    """checks auth"""
    p = {
        "hwid": hwid
    }
    r = requests.get("https://api.novuh.dev/aurtemp/auth", params=p)
    if r.status_code == 200:
        return True
    elif r.status_code == 403:
        return False
    else:
        return False

def get_hwid() -> str:
    """Returns the current machine's hardware ID."""
    uuid = str(subprocess.check_output('wmic csproduct get uuid'))
    pos1 = uuid.find("\\n") + 2
    uuid = uuid[pos1:-15]
    return uuid

def version() -> dict:
    r = requests.get("https://novuh.dev/aurora/version.json")
    return r.json()

