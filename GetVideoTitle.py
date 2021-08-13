import requests
import re
import json
import bv_dec_or_enc as bv

def GetVideoTitle(id_, headers):
    if 'BV' in str(id_):
        bid = id_
    else:
        bid = bv.enc(int(str(id_).replace("av","").replace("AV","").replace("aV","").replace("Av","")))
    
    api_info_url = "http://api.bilibili.com/x/web-interface/view?bvid=%s"%(str(bid))
    req = requests.get(url=api_info_url, headers = headers, verify=False)
    json_ = json.loads(req.text)['data']
    title = re.sub(r"[\/\\\:\*\?\"\<\>\|]","_",json_["title"])
    return title