import time
import requests
import re
import json
import bv_dec_or_enc as bv
from GetVideoCID import GetVideoCid
from GetVideoTitle import GetVideoTitle
import dm_protobuf.dm_pb2 as dm_pb2
import google.protobuf.text_format as text_format
import json
import Sqlite3_Bilibili

def GetAllDanmuInfo(id_, headers):
    if 'BV' in str(id_):
        aid = bv.dec(id_)
    else:
        aid = str(id_).upper().replace("AV","")

    web_url = "https://www.bilibili.com/video/av%s"%(str(aid))
    start_time_req = requests.get(url=web_url, headers = headers, verify=False)
    try:
        req = requests.get(url="https://api.bilibili.com/x/web-interface/archive/stat?aid=%s"%(str(aid)), headers = headers, verify=False)
        if json.loads(req.text)['data']["his_rank"] != 0: # 是否上过每日视频播放排行榜
            infos = re.findall(r'<meta itemprop="uploadDate" content="(.*)" data-vue-meta="true">', start_time_req.text)[0]
        else:
            infos = re.findall(r'<meta data-vue-meta="true" itemprop="uploadDate" content="(.*)"><meta data-vue-meta="true" itemprop="datePublished"', start_time_req.text)[0]
        
    except:
        return None
    
    cid_num = GetVideoCid(aid, headers)
    start_time = re.findall(r"(\d{4}-\d{1,2})",infos)[0]
    time_list = []
    start_time_year = int(re.findall(r"(\d{4})",start_time)[0])
    start_time_month = int(re.findall(r"(-\d{1,2})",start_time)[0].replace("-",""))
    end_time_year = int(time.strftime('%Y',time.localtime(time.time())))
    end_time_month = int(time.strftime('%m',time.localtime(time.time())))
    if start_time_month == end_time_month and start_time_year == end_time_year:
        if len(str(start_time_month)) == 1:
            temp_start_time_month = '0'+str(start_time_month)
        else:
            temp_start_time_month = str(start_time_month)
        get_time_url = "https://api.bilibili.com/x/v2/dm/history/index?type=1&oid=%s&month=%s-%s"%(str(cid_num),str(start_time_year),str(temp_start_time_month))
        req = requests.get(url=get_time_url, headers = headers, verify=False)
        get_time_date_json = json.loads(req.text)['data']
        for time_date in get_time_date_json:
            time_list.append(time_date)

        Database = Sqlite3_Bilibili.Bilibili_Danmu_Server("root", "root", str(cid_num) + ".db")
        Index_Database = Sqlite3_Bilibili.Bilibili_Danmu_Index_Server("root", "root")

        Index_Database_Data = {"cid": int(cid_num), "title": GetVideoTitle(aid, headers), "aid": aid, "bvid":bv.enc(int(aid))}
        Index_Database.Add_Danmu_Database_Info(Index_Database_Data)

        for i in time_list:
            get_his_danmu_url = f"https://api.bilibili.com/x/v2/dm/web/history/seg.so?type=1&oid={str(cid_num)}&date={str(i)}"
            req = requests.get(url=get_his_danmu_url, headers = headers, verify=False)

            # https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/danmaku/history.md
            # https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/grpc_api/bilibili/community/service/dm/v1/dm.proto
            danmaku_seg = dm_pb2.DmSegMobileReply()
            danmaku_seg.ParseFromString(req.content)

            for i in range(len(danmaku_seg.elems)):
                damnu_data = text_format.MessageToString(danmaku_seg.elems[i],as_utf8=True).replace("\n",",")[0:-1].split(",")
                damnu_data_json = dict()
                for a in damnu_data:
                    if len(a.split(": ")[1].split('"',1)) == 1:
                        damnu_data_json[a.split(": ")[0]] = int(a.split(": ")[1])
                    else:
                        damnu_data_json[a.split(": ")[0]] = a.split(": ")[1][1:-1]

                Database.Add_Danmu_Info(damnu_data_json)
    
    else:
        for i in range(abs((start_time_year - end_time_year) * 12 + (start_time_month - end_time_month) * 1) + 1):
            if len(str(start_time_month)) == 1:
                temp_start_time_month = '0'+str(start_time_month)
            else:
                temp_start_time_month = str(start_time_month)
            get_time_url = "https://api.bilibili.com/x/v2/dm/history/index?type=1&oid=%s&month=%s-%s"%(str(cid_num),str(start_time_year),str(temp_start_time_month))
            req = requests.get(url=get_time_url, headers = headers, verify=False)
            if json.loads(req.text)['data'] != None:
                get_time_date_json = json.loads(req.text)['data']
                for time_date in get_time_date_json:
                    time_list.append(time_date)
                if start_time_month == 12:  
                    if start_time_year != end_time_year:
                        start_time_year += 1
                    start_time_month = 1
                else:
                    start_time_month += 1

            for i in time_list:
                get_his_danmu_url = "https://api.bilibili.com/x/v2/dm/history?type=1&oid=%s&date=%s"%(str(cid_num),str(i))
                print(get_his_danmu_url)
                req = requests.get(url=get_his_danmu_url, headers = headers, verify=False)

