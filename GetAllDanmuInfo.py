import time
import requests
import calendar
import re
import json
import bv_dec_or_enc as bv
from GetVideoCID import GetVideoCid
from GetVideoTitle import GetVideoTitle
import dm_protobuf.dm_pb2 as dm_pb2
import google.protobuf.text_format as text_format
import json
import Sqlite3_Bilibili

#关闭requests模块的InsecureRequestWarning警告提示
#from：https://www.cnblogs.com/milian0711/p/6836384.html
#此处 VS Code 报错为正常现象
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def GetAllDanmuInfo(id_, headers):
    if 'BV' in str(id_):
        aid = bv.dec(id_)
    else:
        aid = str(id_).upper().replace("AV","")

    web_url = "https://www.bilibili.com/video/av%s"%(str(aid))
    start_time_req = requests.get(url=web_url, headers = headers, verify=False)
    try:
        req = requests.get(url="https://api.bilibili.com/x/web-interface/archive/stat?aid=%s"%(str(aid)), headers = headers, verify=False)
        # if json.loads(req.text)['data']["his_rank"] != 0: # 是否上过每日视频播放排行榜
        #     infos = re.findall(r'<meta itemprop="uploadDate" content="(.*)" data-vue-meta="true">', start_time_req.text)[0]
        # else:
        #     infos = re.findall(r'<meta data-vue-meta="true" itemprop="uploadDate" content="(.*)"><meta data-vue-meta="true" itemprop="datePublished"', start_time_req.text)[0]
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
        if req.status_code == 200:
            get_time_date_json = json.loads(req.text)['data']
            for time_date in get_time_date_json:
                time_list.append(time_date)
        else: # 预防412错误
            mouth_total_days = calendar.monthrange(start_time_year, start_time_month)[1]
            for i in range(int(mouth_total_days) - int(re.findall(r"(-\d{1,2})",infos)[1].replace("-","")) + 1):
                time_list.append(start_time_year + "-" + temp_start_time_month + "-" + str(int(re.findall(r"(-\d{1,2})",infos)[1].replace("-","")) + i))

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
        Index_Database = Sqlite3_Bilibili.Bilibili_Danmu_Index_Server("root", "root")
        try: 
            Index_Database.cur.execute(f"select * FROM Danmu_Database_Info WHERE cid = {int(cid_num)}")
            Last_End_Time_Year = str(Index_Database.cur.fetchall()[0][4]).split("-")[0]
            Last_End_Time_Mouth = str(Index_Database.cur.fetchall()[0][4]).split("-")[1]
            Last_End_Time_Day = str(Index_Database.cur.fetchall()[0][4]).split("-")[2]

            try:
                start_time_year = int(Last_End_Time_Year)
                start_time_month = int(Last_End_Time_Mouth) + 1

                get_time_url = "https://api.bilibili.com/x/v2/dm/history/index?type=1&oid=%s&month=%s-%s"%(str(cid_num),str(start_time_year),str(Last_End_Time_Mouth))
                req = requests.get(url=get_time_url, headers = headers, verify=False)

                if len(json.loads(req.text)['data']) % 2 != 0:
                    temp_list = json.loads(req.text)['data']
                    for i in range(len(temp_list)):
                        if int(str(temp_list[i]).split("-")[2]) == int(Last_End_Time_Day):
                            time_list = temp_list[i:-1]
                            break

            except: # 当遇到412错误
                start_time_year = int(Last_End_Time_Year)
                start_time_month = int(Last_End_Time_Mouth)

        except:
            pass

        for i in range(abs((start_time_year - end_time_year) * 12 + (start_time_month - end_time_month) * 1) + 1):
            if len(str(start_time_month)) == 1:
                temp_start_time_month = '0'+str(start_time_month)
            else:
                temp_start_time_month = str(start_time_month)
            get_time_url = "https://api.bilibili.com/x/v2/dm/history/index?type=1&oid=%s&month=%s-%s"%(str(cid_num),str(start_time_year),str(temp_start_time_month))
            req = requests.get(url=get_time_url, headers = headers, verify=False)
            if req.status_code == 412: # 当请求被412拒绝时，直接跳出使用本地生成
                break
 
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

        Database = Sqlite3_Bilibili.Bilibili_Danmu_Server("root", "root", str(cid_num) + ".db")

        # 预防 B站获取弹幕保存日期信息API 412 错误，本地生成日期列表
        if len(time_list) == 0 or req.status_code == 412: # B站获取弹幕保存日期信息API不可用
            temp_mouth_dict = {}
            
            while True:
                if start_time_year == end_time_year and start_time_month == end_time_month + 1:
                    break     

                temp_mouth_dict[str(f"{start_time_year}-{start_time_month}")] = calendar.monthrange(start_time_year, start_time_month)[1]

                if start_time_month == 12:  
                    if start_time_year != end_time_year:
                        start_time_year += 1
                    start_time_month = 1
                else:
                    start_time_month += 1

            # 恢复变量内容
            start_time_year = int(re.findall(r"(\d{4})",start_time)[0])
            start_time_month = int(re.findall(r"(-\d{1,2})",start_time)[0].replace("-",""))
                
            for i in list(temp_mouth_dict.keys()):
                for a in range(temp_mouth_dict[i]):
                    if int(i.split("-")[0]) == end_time_year and int(i.split("-")[1]) == end_time_month:
                        if a + 1 > int(time.strftime('%d',time.localtime(time.time()))):
                            break
                        else:
                            if a < 9:
                                if len(str(i.split("-")[1])) == 2:
                                    time_list.append(str(i) + "-0" + str(a + 1))
                                else:
                                    time_list.append(str(i.split("-")[0]) + "-0" + str(i.split("-")[1]) + "-0" + str(a + 1))
                            else:
                                if len(str(i.split("-")[1])) == 2:
                                    time_list.append(str(i) + "-" + str(a + 1))
                                else:
                                    time_list.append(str(i.split("-")[0]) + "-0" + str(i.split("-")[1]) + "-" + str(a + 1))
                    
                    elif int(i.split("-")[0]) == start_time_year and int(i.split("-")[1]) == start_time_month:
                        if a + 1 < int(re.findall(r"(-\d{1,2})",infos)[1].replace("-","")):
                            pass
                        else:
                            if a < 9:
                                if len(str(i.split("-")[1])) == 2:
                                    time_list.append(str(i) + "-0" + str(a + 1))
                                else:
                                    time_list.append(str(i.split("-")[0]) + "-0" + str(i.split("-")[1]) + "-0" + str(a + 1))
                            else:
                                if len(str(i.split("-")[1])) == 2:
                                    time_list.append(str(i) + "-" + str(a + 1))
                                else:
                                    time_list.append(str(i.split("-")[0]) + "-0" + str(i.split("-")[1]) + "-" + str(a + 1))
                    
                    else:
                        if a < 9:
                            if len(str(i.split("-")[1])) == 2:
                                time_list.append(str(i) + "-0" + str(a + 1))
                            else:
                                time_list.append(str(i.split("-")[0]) + "-0" + str(i.split("-")[1]) + "-0" + str(a + 1))
                        else:
                            if len(str(i.split("-")[1])) == 2:
                                time_list.append(str(i) + "-" + str(a + 1))
                            else:
                                time_list.append(str(i.split("-")[0]) + "-0" + str(i.split("-")[1]) + "-" + str(a + 1))


        Index_Database_Data = {"cid": int(cid_num), "title": GetVideoTitle(aid, headers), "aid": aid, "bvid":bv.enc(int(aid)), "Archive_point":str(time_list[0])}
        Index_Database.Add_Danmu_Database_Info(Index_Database_Data)

        for i in time_list:
            flag = 0
            get_his_danmu_url = f"https://api.bilibili.com/x/v2/dm/web/history/seg.so?type=1&oid={str(cid_num)}&date={str(i)}"
            try:
                req = requests.get(url=get_his_danmu_url, headers = headers, verify=False)
            except:
                error_retry_num = 0
                while req.status_code != 200:
                    if error_retry_num >= 10:
                        print(f"{str(i)} 弹幕重试次数过多，跳过该日弹幕。")
                        flag = 1
                        continue

                    print(f"爬取 {str(i)} 弹幕出现错误，3秒后重试，重试次数：{str(error_retry_num)}")
                    time.sleep(3)
                    try:
                        req = requests.get(url=get_his_danmu_url, headers = headers, verify=False)
                    except:
                        pass
                    error_retry_num = error_retry_num + 1

            if flag == 1: # 获取历史弹幕重试次数过多
                continue

            # https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/danmaku/history.md
            # https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/grpc_api/bilibili/community/service/dm/v1/dm.proto
            danmaku_seg = dm_pb2.DmSegMobileReply()
            danmaku_seg.ParseFromString(req.content)

            for i in range(len(danmaku_seg.elems)):
                damnu_data = text_format.MessageToString(danmaku_seg.elems[i],as_utf8=True).split("\n")[0:-1]
                print(damnu_data)
                damnu_data_json = dict()
                for a in damnu_data:
                    if len(a.split(": ")[1].split('"',1)) == 1:
                        damnu_data_json[a.split(": ")[0]] = int(a.split(": ")[1])
                    else:
                        damnu_data_json[a.split(": ")[0]] = a.split(": ")[1][1:-1]

                Database.Add_Danmu_Info(damnu_data_json)
                Index_Database.Set_Archive_point(str(i), cid_num)

        Database.Close_Database()
        Index_Database.Close_Database()