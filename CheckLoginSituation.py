import requests

def CheckLoginSituation(headers):
    req = requests.get(url="https://space.bilibili.com/", headers = headers, verify=False)

    if "passport" in req.url:
        return 1
    else:
        return 0