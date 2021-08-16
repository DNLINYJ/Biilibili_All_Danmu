import requests
import re
import json

def RemoteBulitTimeList(start_time_year, start_time_month, start_time_day, end_time_year, end_time_month, cid_num, headers):
    time_list = list()

    for i in range(abs((start_time_year - end_time_year) * 12 + (start_time_month - end_time_month) * 1) + 1):
        if len(str(start_time_month)) == 1:
            temp_start_time_month = '0'+str(start_time_month)
        else:
            temp_start_time_month = str(start_time_month)
        get_time_url = "https://api.bilibili.com/x/v2/dm/history/index?type=1&oid=%s&month=%s-%s"%(str(cid_num),str(start_time_year),str(temp_start_time_month))
        try:
            req = requests.get(url=get_time_url, headers = headers, verify=False)
        except:
            continue
        if req.status_code != 200: # 当请求被拒绝时，直接跳出使用本地生成
            return None

        if json.loads(req.text)['code'] == -101:
            print("B站账号未登录,无法获取历史弹幕!")
            return 1

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
        else:
            pass

    # 修复远程构建历史弹幕时间列表 无法根据上次最后存档点 断点续传的BUG
    for i in range(len(time_list)):
        if start_time_year == int(re.findall(r"(\d{4})", time_list[i])[0]):
            if start_time_month == int(re.findall(r"(-\d{1,2})", time_list[i])[0].replace("-","")):
                if start_time_day == int(re.findall(r"(-\d{1,2})", time_list[i])[1].replace("-","")):
                    time_list = time_list[i::]
    
    return time_list