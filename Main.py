from GetAllDanmuInfo_V2 import GetAllDanmuInfo
from GetClearCommandInstruction import GetClearCommandInstruction
from GetVideoTitle import GetVideoTitle
from ExportAllDanmu import ExportAllDanmu
from CheckLoginSituation import CheckLoginSituation
import base64
import Sqlite3_Bilibili
import sys
import os

headers = {
        'cookie': "",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://www.bilibili.com'
}

def isnum(n):
    try:
        float(int(n))
        return True
    except:
        return False

def FromUrlGetAidOrBvid(video_url):
    base_url_list = [
        "https://www.bilibili.com/video/"
    ]
    if "http" in video_url:
        for i in range(len(base_url_list)):
            if base_url_list[i] in video_url:
                return str(video_url).replace(base_url_list[i],"").split("?",1)[0].replace("/","")

    return video_url

def Meum():
    if os.path.exists("sqlite3") == False:
            os.makedirs("sqlite3")
    if os.path.exists("Export") == False:
            os.makedirs("Export")
            
    clear_comand_instruction = GetClearCommandInstruction()
    Index_Server = Sqlite3_Bilibili.Bilibili_Danmu_Index_Server("root", "root")

    if os.path.exists(".config") == False:
        while True:
            print("检测到您第一次使用本程序,请输入您的SESSDATA便于接下来的操作")
            print("若不清楚自己的SESSDATA的话,请查看README中的教程链接解决该问题")
            print("格式为：SESSDATA=您获取的SESSDATA")
            user_input = input(">>")

            if "SESSDATA=" in user_input.upper():
                with open(".config", "w", encoding="utf-8") as f:
                    f.write(base64.b64encode(user_input.encode("utf-8")).decode())
                break
            else:
                print("请输入正确格式的SESSDATA!")
                os.system(clear_comand_instruction)
    
    else:
        with open(".config","r",encoding="utf-8") as f:
            temp_sessdata = f.read()
        temp_sessdata = base64.b64decode(temp_sessdata).decode()
        headers["cookie"] = temp_sessdata
        while CheckLoginSituation(headers) == 1:
            os.system(clear_comand_instruction)
            print("SESSDATA已过期,请重新输入您的SESSDATA")
            print("若不清楚自己的SESSDATA的话,请查看README中的教程链接解决该问题")
            print("格式为：SESSDATA=您获取的SESSDATA")
            user_input = input(">>")

            if "SESSDATA=" in user_input.upper():
                with open(".config", "w", encoding="utf-8") as f:
                    f.write(base64.b64encode(user_input.encode("utf-8")).decode())
                headers["cookie"] = temp_sessdata
            else:
                print("请输入正确格式的SESSDATA!")
                os.system(clear_comand_instruction)

    while True:
        os.system(clear_comand_instruction)

        while CheckLoginSituation(headers) == 1:
            if os.path.exists(".config") == True:
                print("SESSDATA已过期,请重新输入您的SESSDATA")
                print("若不清楚自己的SESSDATA的话,请查看README中的教程链接解决该问题")
                print("格式为：SESSDATA=您获取的SESSDATA")
                user_input = input(">>")

                if "SESSDATA=" in user_input.upper():
                    with open(".config", "w", encoding="utf-8") as f:
                        f.write(base64.b64encode(user_input.encode("utf-8")).decode())
                    headers["cookie"] = user_input
                else:
                    print("请输入正确格式的SESSDATA!")
                    os.system(clear_comand_instruction)

            else:
                print("警告!!!未登录!!!无法获取历史弹幕!!!")
                print("请查看文档进行登录!!")
                input("按下任意键退出...")
                sys.exit(0)

        print("Bilibili(B站)全弹幕获取程序")
        print("作者：菠萝小西瓜(DNLINYJ)")
        print("Github：https://github.com/DNLINYJ")
        print("注意：仅供个人学习交流使用，切勿用于非法用途！")
        print("---------------------------------------------------------")
        print("1) 收集指定视频全部历史弹幕(数据量较大时所用时间较久)")
        print("2) 导出数据库内指定视频全部历史弹幕")
        print("3) 收集并导出指定视频全部历史弹幕(数据量较大时所用时间较久,谨慎使用)")
        print("4) 退出")
        user_input = str(input(">>"))
        if user_input == "1":
            os.system(clear_comand_instruction)

            print("请输入B站视频的AV号/BV号,或者输入B站视频地址(仅支持单P视频/多P视频中的单P下载)")
            user_input = str(input(">>"))

            user_input = FromUrlGetAidOrBvid(user_input)
            result = GetAllDanmuInfo(user_input, headers)
            if result == 0:
                print(f"获取视频：{GetVideoTitle(user_input, headers)} 的所有历史弹幕成功.")
                input("按下任意键继续...")
            elif result == 2:
                input("按下任意键继续...")
            else:
                print(f"获取视频：{GetVideoTitle(user_input, headers)} 的所有历史弹幕失败.")
                input("按下任意键继续...")
                
        elif user_input == "2":
            os.system(clear_comand_instruction)

            Video_Info_List = Index_Server.GetAllVideoDatabaseName()
            
            if Video_Info_List != None:
                print("历史弹幕数据库中存在的视频如下:")
                print("-----------------------------------------------------------")

                for i in range(len(Video_Info_List)):
                    print(f"{i + 1}) 视频标题:{Video_Info_List[i][1]} 视频AV号:{Video_Info_List[i][2]} 保存的弹幕结束日期:{Video_Info_List[i][4]}")
                
                print("-----------------------------------------------------------")

                print("请输入您想导出的视频序号")
                user_input = input(">>")

                if isnum(user_input) == False:
                    print("请输入正确的选项!")
                    input("按下回车继续运行...")
                    os.system(clear_comand_instruction)

                else:
                    if int(user_input) > len(Video_Info_List):
                        print("请输入正确的选项!")
                        input("按下回车继续运行...")
                    else:
                        ExportAllDanmu(Video_Info_List[int(user_input) - 1][2])
                        input("按下回车继续运行...")
                        os.system(clear_comand_instruction)
            
            else:
                print("历史弹幕数据库中无可用视频历史弹幕可导出!")
                input("按下回车继续运行...")
                os.system(clear_comand_instruction)

        elif user_input == "3":
            os.system(clear_comand_instruction)

            print("请输入B站视频的AV号/BV号,或者输入B站视频地址(仅支持单P视频/多P视频中的单P下载)")
            user_input = str(input(">>"))

            user_input = FromUrlGetAidOrBvid(user_input)
            result = GetAllDanmuInfo(user_input, headers)
            if result == 0:
                print(f"获取视频{GetVideoTitle(user_input, headers)} 的所有历史弹幕成功.")
                ExportAllDanmu(user_input)
                input("按下任意键继续...")
            elif result == 2:
                input("按下任意键继续...")
            else:
                print(f"获取视频{GetVideoTitle(user_input, headers)} 的所有历史弹幕失败.")
                input("按下任意键继续...")

        elif user_input == "4":
            sys.exit(0)


if __name__ == '__main__':
    Meum()