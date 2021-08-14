import Sqlite3_Bilibili
import time
import re

def ExportAllDanmu(id_num):
    cid = Sqlite3_Bilibili.Bilibili_Danmu_Index_Server("root","root").Find_Cid(id_num)[0][0]
    title = Sqlite3_Bilibili.Bilibili_Danmu_Index_Server("root","root").Find_Cid(id_num)[0][1]
    Danmu_Database = Sqlite3_Bilibili.Bilibili_Danmu_Server("root", "root", str(cid) + ".db")

    Base_XML = InitXmlFile(cid)
    Total_Danmu_Num = 0
    All_TABLE = Danmu_Database.Read_All_TABLE()
    for i in All_TABLE:
        for a in Danmu_Database.Read_TABLE_All_Data(i[0]):
            Danmu_XML = f'<d p="{str(round(a[2]/1000, 5))},{str(a[3])},{str(a[4])},{str(a[5])},{str(a[8])},0,{str(a[6])},{str(a[1])}">{str(a[7])}</d>'
            Base_XML = Base_XML + Danmu_XML
            Total_Danmu_Num = Total_Danmu_Num + 1
    
    Base_XML.replace("<maxlimit>1000</maxlimit>", f"<maxlimit>{str(Total_Danmu_Num)}</maxlimit>", 1)
    Base_XML = Base_XML + "</i>"

    Export_Filename = f'{title}_全弹幕导出_{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}.Xml'
    Export_Filename = re.sub(r"[\/\\\:\*\?\"\<\>\|]","_", Export_Filename)
    with open("Export/" + Export_Filename,"w",encoding="utf-8") as f:
        f.write(Base_XML)

def InitXmlFile(cid):
    base_xml = f"<i><chatserver>chat.bilibili.com</chatserver><chatid>{cid}</chatid><mission>0</mission><maxlimit>1000</maxlimit><state>0</state><real_name>0</real_name><source>k-v</source>"
    return base_xml

ExportAllDanmu('BV1wo4y1U7VS')