import time
import requests
import re
import bv_dec_or_enc as bv
from GetVideoCID import GetVideoCid
from GetVideoTitle import GetVideoTitle
from LocalBulitTimeList import LocalBulitTimeList
from RemoteBulitTimeList import RemoteBulitTimeList
import dm_protobuf.dm_pb2 as dm_pb2
from google.protobuf.json_format import MessageToDict
import Sqlite3_Bilibili

#关闭requests模块的InsecureRequestWarning警告提示
#from：https://www.cnblogs.com/milian0711/p/6836384.html
#此处 VS Code 报错为正常现象
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# From: https://www.cnpython.com/qa/58810
def remove_bad_chars(string):
    #all unicode characters from 0x0000 - 0x0020 (33 total) are bad and will be replaced by "" (empty string)
    temp_list = list(string)
    for pos in range(len(temp_list)):
        if ord(temp_list[pos]) < 32:
            temp_list[pos] = ""
        return ''.join(temp_list)

def GetAllDanmuInfo(id_, headers):
    if 'BV' in str(id_):
        bvid = id_
    else:
        bvid = bv.enc(int(str(id_).upper().replace("AV","")))

    # 获得视频投稿时间
    web_url = f"https://www.bilibili.com/video/{bvid}"
    start_time_req = requests.get(url=web_url, headers = headers, verify=False)

    # 使用正则表达式获得视频投稿时间
    try: 
        infos = re.findall(r'<meta data-vue-meta="true" itemprop="uploadDate" content="(.*)"><meta data-vue-meta="true" itemprop="datePublished"', start_time_req.text)[0]
    except:
        return None

    # 获得视频CID号
    cid_num = GetVideoCid(bvid, headers)

    # 获取CID时发生错误
    if cid_num == None:
        return 2

    # 获得视频标题
    Video_title = GetVideoTitle(bvid, headers)

    # 检测是否为分P视频
    if type(cid_num) == list:
        Video_title = Video_title + " - " + cid_num[1]
        cid_num = cid_num[2]

    # 获得历史弹幕时间列表的时间范围
    start_time_year = int(re.findall(r"(\d{4})", infos)[0])
    start_time_month = int(re.findall(r"(-\d{1,2})", infos)[0].replace("-",""))
    start_time_day = int(re.findall(r"(-\d{1,2})", infos)[1].replace("-",""))
    
    end_time_year = int(time.strftime('%Y',time.localtime(time.time())))
    end_time_month = int(time.strftime('%m',time.localtime(time.time())))
    end_time_day = int(time.strftime('%d',time.localtime(time.time())))
    
    # 初始化历史弹幕数据库和索引数据库 数据库用户名和密码默认为 root/root
    # 历史弹幕数据库
    Database = Sqlite3_Bilibili.Bilibili_Danmu_Server("root", "root", f"{str(cid_num)}.db")
    # 索引数据库
    Index_Database = Sqlite3_Bilibili.Bilibili_Danmu_Index_Server("root", "root")

    # 若数据库中有现处理视频的数据，读取上次最后写入的历史弹幕的日期
    ReadLastEndTime = Index_Database.ReadLastEndTime(bvid)
    if ReadLastEndTime:
        start_time_year = int(re.findall(r"(\d{4})", ReadLastEndTime[0][0])[0])
        start_time_month = int(re.findall(r"(-\d{1,2})", ReadLastEndTime[0][0])[0].replace("-",""))
        start_time_day = int(re.findall(r"(-\d{1,2})", ReadLastEndTime[0][0])[1].replace("-",""))

    # 远程构建时间范围列表
    Time_list = RemoteBulitTimeList(
        start_time_year,
        start_time_month,
        start_time_day,
        end_time_year,
        end_time_month,
        cid_num,
        headers
    )

    # 若远程构建时间范围列表出现B站服务器拒绝访问，使用本地构建
    if Time_list == None or Time_list == []:
        Time_list = LocalBulitTimeList(
            start_time_year,
            start_time_month,
            start_time_day,
            end_time_year,
            end_time_month,
            end_time_day
        )

    # 若B站账号未登录
    elif Time_list == 1:
        return None

    # 向索引数据库中插入历史弹幕数据库的基本信息
    Index_Database_Data = {
        "cid": int(cid_num),
        "title": Video_title,
        "aid": bv.dec(bvid),
        "bvid": bvid,
        "Archive_point": str(Time_list[0])}
    Index_Database.Add_Danmu_Database_Info(Index_Database_Data)

    # 设置一个假栈,用于还原变量
    Stack = list()

    # 遍布时间列表，获取历史弹幕
    for i in Time_list:
        # 输出日志
        print(f"正在获取视频:{Video_title} 于{str(i)} 的历史弹幕")
        Stack.append(str(i))

        # 设置最后读取的历史弹幕的日期, 便于断点续传
        Index_Database.Set_Archive_point(str(i), cid_num)

        # 是否跳过当前日期的历史弹幕
        Jump_Out_Flag = 0

        # 获取历史弹幕文件
        get_his_danmu_url = f"https://api.bilibili.com/x/v2/dm/web/history/seg.so?type=1&oid={str(cid_num)}&date={str(i)}"
        req = requests.get(url = get_his_danmu_url, headers = headers, verify=False)

        # 获取弹幕文件出错
        if req.status_code != 200:
            Retry_Num = 0
            if req.status_code == 412:
                print("B站请求被拦截,暂停本次获取操作.")
                return 1
            while req.status_code != 200:

                # 重试次数超过2次,直接抛弃该日历史弹幕数据
                if Retry_Num >= 2:
                    print(f"获取视频:{Video_title} 于{str(i)} 的历史弹幕失败,将跳过该日历史弹幕数据。")
                    Retry_Num = 0
                    Jump_Out_Flag = 1
                    break
                
                print(f"获取视频:{Video_title} 于{str(i)} 的历史弹幕失败,将于3秒后重试,重试次数:{str(Retry_Num)}")
                time.sleep(3)
                Retry_Num += 1
                req = requests.get(url=get_his_danmu_url, headers = headers, verify=False)

        # 跳过当前日期的历史弹幕
        if Jump_Out_Flag == 1:
            # 标识符归位
            Jump_Out_Flag = 0
            continue

        # 使用Protobuf脚本解码B站弹幕文件
        # From 1:https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/danmaku/history.md
        # From 2:https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/grpc_api/bilibili/community/service/dm/v1/dm.proto
        # From 3:https://stackoverflow.com/questions/19734617/protobuf-to-json-in-python
        danmaku_seg = dm_pb2.DmSegMobileReply()
        danmaku_seg.ParseFromString(req.content)

        # 将弹幕文件解码为数据库支持的格式
        for i in range(len(danmaku_seg.elems)):
            damnu_data = MessageToDict(danmaku_seg.elems[i])

            # 去除XML文件不能解析的字符
            damnu_data["content"] = remove_bad_chars(damnu_data["content"])

            # 将历史弹幕数据插入数据库
            Database.Add_Danmu_Info(damnu_data)

        # 输出日志
        print(f"获取视频:{Video_title} 于{str(Stack[0])} 的历史弹幕成功")

        # 清空栈
        Stack.clear()

    return 0