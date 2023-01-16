import sqlite3
import base64
import time
import bv_dec_or_enc as bv
# https://www.cnblogs.com/desireyang/p/12102143.html

class Bilibili_Danmu_Server():
    def __init__(self, username, password, database_file):
        #Set base information
        self.username = username
        self.password = password
        self.database_file = "sqlite3/" + database_file

        # Init Sqlite3 database
        if ".DB" not in str(self.database_file).upper():
            self.server_connent = sqlite3.connect(self.database_file + ".db")
        else:
            self.server_connent = sqlite3.connect(self.database_file)
        
        # Set Server Cursor
        self.cur = self.server_connent.cursor()

    def Add_Danmu_Info(self, damnu_data):
        TABLE_time = time.strftime("%Y%m%d", time.localtime(int(damnu_data["ctime"])))
        init_sql = f"CREATE TABLE IF NOT EXISTS Danmu_{TABLE_time}(num INTEGER PRIMARY KEY, id INT8, progress INTEGER, mode INTEGER, fontsize INTEGER, color INTEGER, midHash TEXT, content TEXT, ctime INT8, idStr TEXT, UNIQUE(id))"
        
        # Init Server Table
        self.cur.execute(init_sql)
        self.server_connent.commit()

        # https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/danmaku/danmaku_proto.md
        # num      INTEGER PRIMARY KEY  弹幕数量
        # id       INT8                 弹幕dmid
        # progress INTEGER              视频内弹幕出现时间
        # mode     INTEGER              弹幕类型
        # fontsize INTEGER              弹幕字号
        # color    INTEGER              弹幕颜色
        # midHash  TEXT                 发送者mid的HASH
        # content  TEXT                 弹幕内容(base64)
        # ctime    INT8                 弹幕发送时间
        # idStr    TEXT                 弹幕dmid

        # Process Danmu Info Data
        Check_Completeness = dict()
        try:
            Check_Completeness = {
                                "id" : int(damnu_data["id"]),
                                "progress" : damnu_data["progress"],
                                "mode" : damnu_data["mode"],
                                "fontsize" : damnu_data["fontsize"],
                                "color" : damnu_data["color"],
                                "midHash" : damnu_data["midHash"],
                                "content" : base64.b64encode(damnu_data["content"].encode()).decode(),
                                "ctime" : int(damnu_data["ctime"]),
                                "idStr" : damnu_data["idStr"],
                                }
        except:
            return None
            
        if Check_Completeness != {}:
            data = str()
            data_keys = list(Check_Completeness.keys())
            for i in data_keys:
                if i == "idStr":
                    if type(Check_Completeness[i]) == str:
                        data = data + f"'{Check_Completeness[i]}'"
                    else:
                        data = data + str(Check_Completeness[i])
                else:
                    if type(Check_Completeness[i]) == str:
                        data = data + f"'{Check_Completeness[i]}',"
                    else:
                        data = data + str(Check_Completeness[i]) + ","
        else:
            return None

        # Add Danmu Data to Server
        try:
            self.cur.execute('INSERT OR IGNORE INTO ' + "Danmu_"+TABLE_time + ' VALUES (NULL, %s)' % data)
        except:
            return None
        self.server_connent.commit()

    def Read_All_TABLE(self):
        self.cur.execute("select name from sqlite_master where type='table' order by name")
        return self.cur.fetchall()

    def Read_TABLE_All_Data(self, Table_name):
        self.cur.execute(f"select * from {Table_name}")
        return self.cur.fetchall()

    def Close_Database(self):
        self.server_connent.close()

class Bilibili_Danmu_Index_Server():
    def __init__(self, username, password):
        #Set base information
        self.username = username
        self.password = password
        self.database_file = "sqlite3/index.db"

        # Init Sqlite3 database
        if ".DB" not in str(self.database_file).upper():
            self.server_connent = sqlite3.connect(self.database_file + ".db")
        else:
            self.server_connent = sqlite3.connect(self.database_file)
        
        # Set Server Cursor
        self.cur = self.server_connent.cursor()

    def Add_Danmu_Database_Info(self, Danmu_Database_Info):
        init_sql = f"CREATE TABLE IF NOT EXISTS Danmu_Database_Info(cid INTEGER PRIMARY KEY, title TEXT, aid INTEGER, bvid TEXT, Archive_point TEXT, UNIQUE(cid))"
        
        # Init Server Table
        self.cur.execute(init_sql)
        self.server_connent.commit()

        # cid           INTEGER PRIMARY KEY  视频CID号
        # title         TEXT                 视频标题
        # aid           INTEGER              视频AV号
        # bvid          TEXT                 视频BVID
        # Archive_point TEXT                 弹幕存储的最后日期

        # Process Danmu Info Data
        data = str()
        data_keys = list(Danmu_Database_Info.keys())
        for i in data_keys:
            if i == len(data_keys) - 1:
                if type(Danmu_Database_Info[i]) == str:
                    data = data + f"'{Danmu_Database_Info[i]}'"
                else:
                    data = data + str(Danmu_Database_Info[i])
            else:
                if type(Danmu_Database_Info[i]) == str:
                    data = data + f"'{Danmu_Database_Info[i]}',"
                else:
                    data = data + str(Danmu_Database_Info[i]) + ","

        # Add Danmu Data to Server
        self.cur.execute('INSERT OR IGNORE INTO Danmu_Database_Info VALUES (%s)' % data[0:-1])
        self.server_connent.commit()

    def Find_Cid(self, id_):
        if 'BV' in str(id_):
            bvid = id_
        else:
            bvid = bv.enc(int(str(id_).upper().replace("AV","")))

        try:
            self.cur.execute(f"select * FROM Danmu_Database_Info WHERE bvid = '{bvid}'")
            return self.cur.fetchall()
        except:
            return None

    def ReadLastEndTime(self, id_):
        if 'BV' in str(id_):
            bvid = id_
        else:
            bvid = bv.enc(int(str(id_).upper().replace("AV","")))

        try:
            self.cur.execute(f"select Archive_point FROM Danmu_Database_Info WHERE bvid = '{bvid}'")
            return self.cur.fetchall()
        except:
            return None

    def Set_Archive_point(self, time_str, cid):
        self.cur.execute(f"UPDATE Danmu_Database_Info SET Archive_point = '{time_str}' WHERE cid = {int(cid)}")
        self.server_connent.commit()

    def GetAllVideoDatabaseName(self):
        try:
            self.cur.execute("select * FROM Danmu_Database_Info")
            return self.cur.fetchall()
        except:
            return None

    def Close_Database(self):
        self.server_connent.close()