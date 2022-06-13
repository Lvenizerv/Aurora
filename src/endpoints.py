from licensing.models import *
from licensing.methods import Key, Helpers
import requests
import subprocess    


#get HWID
def GetUUID():
   cmd = 'wmic csproduct get uuid'
   uuid = str(subprocess.check_output(cmd))
   pos1 = uuid.find("\\n")+2
   uuid = uuid[pos1:-15]
   return uuid

#auth check
def auth(my_key:str,have_license=True)-> bool:
    RSAPubKey = "<RSAKeyValue><Modulus>zdGKfx2Xsp39NJQ6Tgpb4i2AQQ9sZOtPrbAe8FBG/9cKBJyYmX4rYQePMxyCM5Gu8tx+gnkh/nl8j4PGRwDSr2szAfBFVKCI1cqyoRFMzxAcj78RIVWD+3GtPj0FHuci+XysjKS0EMp6nXSr6sv7Mf/66QvSa1tXeKuk7ZUo0Ipd74IGc/UHelIki2VCCYvFNf7Ml9k6JRHCegfWW0AV57K/xkIOtUzopOoKZrXnEvuUnHmQU6XN4cMulPR0ifjVMS6QHN3/YJuO+GQsYXfHh5WDy9ql/wgWMExbTpKl0mYu9cK8Ulu0EIfZcw+Q+MPU2/UlclVf1Zm4skWGFBCkvw==</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>"
    auth = "WyI1MzE5NzI1Iiwia3luWlQ4TjJUZDkxRmIrVzJVc0lxT0h1QkljMEdyWmJ4aExRaGRYQiJd"
    result = Key.activate(token=auth,\
                       rsa_pub_key=RSAPubKey,\
                       product_id=14368, \
                       key=my_key,\
                       machine_code=GetUUID())
    if result[0] == None:
        return {'bool':False,'answer':format(result[1])}
    else:
        if have_license==False:
            with open('license.txt','w')as f:f.write(my_key)
        return True
    


#Redeem acts as auth no need for this
#def auth(hwid: str) -> bool:
#    """checks auth"""
#    with open('license.skm', 'r') as f:
#        license_key = LicenseKey.load_from_string(RSAPubKey, f.read())
#        if license_key == None or not Helpers.IsOnRightMachine(license_key):
#            return False
#        else:
#            return True

def version() -> dict:
    r = requests.get("https://api.auroratools.shop/data.json")
    return r.json()
