import requests
import re
import json
import bv_dec_or_enc as bv

#关闭requests模块的InsecureRequestWarning警告提示
#from：https://www.cnblogs.com/milian0711/p/6836384.html
#此处 VS Code 报错为正常现象
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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