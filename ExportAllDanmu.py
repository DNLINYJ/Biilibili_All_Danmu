import Sqlite3_Bilibili
import time
import re
import base64

def ExportAllDanmu(id_num):
    cid = Sqlite3_Bilibili.Bilibili_Danmu_Index_Server("root","root").Find_Cid(id_num)[0][0]
    title = Sqlite3_Bilibili.Bilibili_Danmu_Index_Server("root","root").Find_Cid(id_num)[0][1]
    Danmu_Database = Sqlite3_Bilibili.Bilibili_Danmu_Server("root", "root", str(cid) + ".db")

    # 打印日志
    print(f"正在导出视频:{title} 的全部历史弹幕.")

    Base_XML_List = InitXmlFile(cid)
    Total_Danmu_Num = 0
    All_TABLE = Danmu_Database.Read_All_TABLE()
    Danmu_XML_Temp_Str = str()
    for i in All_TABLE:
        for a in Danmu_Database.Read_TABLE_All_Data(i[0]):
            Temp_Str = str(base64.b64decode(a[7]).decode()).replace("<","&lt;").replace(">","&gt;").replace("&","&amp;").replace("\'","&apos;").replace("\"","&quot;")
            Danmu_XML = f'<d p="{str(round(a[2]/1000, 5))},{str(a[3])},{str(a[4])},{str(a[5])},{str(a[8])},0,{str(a[6])},{str(a[1])}">{Temp_Str}</d>'
            Danmu_XML_Temp_Str = Danmu_XML_Temp_Str + Danmu_XML
            Total_Danmu_Num = Total_Danmu_Num + 1
    
    Base_XML = Base_XML_List[0] + str(Total_Danmu_Num) + Base_XML_List[1] + Danmu_XML_Temp_Str + "</i>"

    Export_Filename = f'{title}_全弹幕导出_{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}.Xml'
    Export_Filename = re.sub(r"[\/\\\:\*\?\"\<\>\|]","_", Export_Filename)
    with open("Export/" + Export_Filename,"w",encoding="utf-8") as f:
        f.write(Base_XML)

    print(f"导出视频:{title} 的全部历史弹幕成功.")

def InitXmlFile(cid):
    base_xml_1 = f"<i><chatserver>chat.bilibili.com</chatserver><chatid>{cid}</chatid><mission>0</mission><maxlimit>"
    base_xml_2 = "</maxlimit><state>0</state><real_name>0</real_name><source>k-v</source>"
    return [base_xml_1, base_xml_2]
