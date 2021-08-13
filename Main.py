from GetAllDanmuInfo import GetAllDanmuInfo
import platform

headers = {
        'cookie': "",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://www.bilibili.com'
}

def Meum():
    clear_comand_instruction = get_clear_comand_instruction()
    print("B站全弹幕获取程序")
    print("作者：菠萝小西瓜(DNLINYJ)")
    print("Github：https://github.com/DNLINYJ")
    print("注意：仅供个人学习交流使用，切勿用于非法用途！")
    print("---------------------------------------------------------")
    print("1) 收集指定视频全部历史弹幕")
    print("2) 导出指定视频全部历史弹幕")
    print("3) 收集并导出指定视频全部历史弹幕(数据量较大时所用时间较久)")
    user_input = str(input(">>"))
    GetAllDanmuInfo("BV1wo4y1U7VS", headers)

def get_clear_comand_instruction():
    a = platform.system()
    if a == "Linux":
        return "clear"
    elif a == "Windows":
        return "cls"
    else:
        return "clear"