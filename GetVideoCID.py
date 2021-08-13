import requests
import json
import bv_dec_or_enc as bv

def GetVideoCid(id_, headers, m=0, p=0): 
    """
        获取Cid/Oid\n

        id_ BV/AV号\n
        m 模式（默认为0[默认]，1为[返回全部分P]）\n
        p 指定返回分P （默认为0[不指定]）\n
        
        (1)单P返回格式: (str)
            "视频cid号"

        (2)多P下载所有返回格式： (dict)
            {"视频标题1":"视频cid号1","视频标题2":"视频cid号2",...,"视频标题n":"视频cid号n"}

        (2)多P下载单P返回格式： (list)
            ["视频P数","视频标题","视频cid号"]

        temp_json['videos']['pages'][i]['part'] 或 json.loads(cid.text)['videos']['pages'][i]['part'] 是分P标题 i是视频P数\n
        Cid 和 Oid 本质上是一样的！！！！
    """

    if 'BV' in str(id_): #将BV/AV号转换为BV号
        bvid = id_
    else:
        bvid = bv.enc(int(str(id_).replace("av","").replace("AV","").replace("aV","").replace("Av","")))

    search_api = f"https://api.bilibili.com/x/player/pagelist?bvid={str(bvid)}"
    cid = requests.get(url=search_api, headers = headers, verify=False)

    if p == 0: #当没有指定P数时（默认）

        if len(json.loads(cid.text)['data']) == 1: #当只有一个视频时
            return str(json.loads(cid.text)['data'][0]["cid"])

        else: #当有多个视频时
            if m == 1: #返回全部分P(函数传入)
                temp_json = json.loads(cid.text)
                temp_dict = {}
                for i in range(len(temp_json["data"])):
                    temp_dict[temp_json['data'][i]['part']] = str(temp_json['data'][i]['cid'])
                return temp_dict

            temp_json = json.loads(cid.text)
            for i in range(len(temp_json['data'])): #输出P数和各自对应的标题
                print("第%sP,标题为：%s"%(str(temp_json['data'][i]["page"]),str(temp_json['data'][i]['part'])))
                # temp_json['data'][i]["page"] 视频P数
                # temp_json['data'][i]['part'] 视频标题

            c_num = str(input("请选择需要的P:(若全选输入ALL)")) #c_num 为视频P数 

            if c_num.upper() == "ALL":
                temp_dict = {}
                for i in range(len(temp_json["data"])):
                    temp_dict[temp_json['data'][i]['part']] = str(temp_json['data'][i]['cid'])
                return temp_dict
            else:
                return [str(c_num),str(temp_json['data'][int(c_num)-1]['part']),str(temp_json['data'][int(c_num)-1]['cid'])]

    else:   # 指定P数时 
            # 多P下载单P返回格式： (list) 
            # ["视频P数","视频标题","视频cid号"]
        return [p, json.loads(cid.text)['data'][int(p)-1]['part'], json.loads(cid.text)['data'][int(p)-1]["cid"]]