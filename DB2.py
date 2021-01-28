import sqlite3


class databaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('./database/local.db')
        self.createTable()
        self.addEntries()

    def createTable(self):
        c = self.conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS Image_views 
        (
        Views TEXT PRIMARY KEY
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS DETAILS 
        (
        Tag_No INTEGER PRIMARY KEY, 
        Description TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS Image 
        (
        Image_Name TEXT NOT NULL, 
        Tag_No INT NOT NULL, 
        PRIMARY KEY(Image_Name,Tag_No), 
        FOREIGN KEY(Tag_No) REFERENCES DETAILS(Tag_No)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS Filter 
        (
        filter_name TEXT PRIMARY KEY, 
        tag_name TEXT,
        Description TEXT, 
        Trainable INTEGER
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS Filter_Session 
        (
        sesID INTEGER PRIMARY KEY AUTOINCREMENT, 
        filter_name TEXT,
        View TEXT,
        Params TEXT,
        time REAL,
        image_amount INT,
        FOREIGN KEY(View) REFERENCES Image_views(Views),
        FOREIGN KEY(filter_name) REFERENCES Filter(filter_name)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS Filter_tag 
        (
        filter_name TEXT, 
        Params TEXT,
        View TEXT,
        tag_alias TEXT,
        tag_name TEXT,
        performance REAL,
        ses_amt INTEGER,
        detectedImage INTEGER,
        FOREIGN KEY(View) REFERENCES Image_views(Views),
        FOREIGN KEY(filter_name) REFERENCES Filter(filter_name),
        PRIMARY KEY(filter_name, Params, View, tag_alias, tag_name)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS Image_tag   
        (
        sesID INTEGER PRIMARY KEY AUTOINCREMENT, 
        image_name TEXT,
        View TEXT,
        detail TEXT,
        
        FOREIGN KEY(View) REFERENCES Image_views(Views),
        FOREIGN KEY(detail) REFERENCES DETAILS(Description)
        )''')
        c.close()

    def addEntries(self):
        c = self.conn.cursor()
        try: 
            c.execute("INSERT into Image_views values('Top')")
            c.execute("INSERT into Image_views values('Bottom')")
            c.execute("INSERT into Image_views values('Left')")
            c.execute("INSERT into Image_views values('Right')")
            self.conn.commit()
        except:
            pass
        try:
            c.execute("INSERT into DETAILS values(2,'dry_neck_label')")
            c.execute("INSERT into DETAILS values(3,'pale_neck_label_but_not_dry')")
            c.execute("INSERT into DETAILS values(4,'label_has_scratch_but_not_dry')")
            c.execute("INSERT into DETAILS values(5,'dirty_wuth_white_fungus_inside')")
            c.execute("INSERT into DETAILS values(6,'dirty_with_black_fungus_inside')")
            c.execute("INSERT into DETAILS values(7,'shallow_scratches_on_shoulder')")
            c.execute("INSERT into DETAILS values(8,'perfect_bottles')")
            c.execute("INSERT into DETAILS values(9,'no_label')")
            c.execute("INSERT into DETAILS values(10,'dry_label')")
            c.execute("INSERT into DETAILS values(11,'straw')")
            c.execute("INSERT into DETAILS values(12,'cigarettes')")
            c.execute("INSERT into DETAILS values(13,'bottle_caps')")
            c.execute("INSERT into DETAILS values(14,'transparent_plastic_bags')")
            c.execute("INSERT into DETAILS values(15,'tissue_paper')")
            c.execute("INSERT into DETAILS values(16,'toothpick')")
            c.execute("INSERT into DETAILS values(17,'wire')")
            c.execute("INSERT into DETAILS values(18,'other_kind_of_trash')")
            c.execute("INSERT into DETAILS values(19,'medical_zip_lock_bag')")
            c.execute("INSERT into DETAILS values(20,'paper')")
            c.execute("INSERT into DETAILS values(21,'opaque_plastic_bag')")
            c.execute("INSERT into DETAILS values(22,'cap_liner')")
            c.execute("INSERT into DETAILS values(23,'cotton_bud')")
            c.execute("INSERT into DETAILS values(24,'sticks')")
            c.execute("INSERT into DETAILS values(25,'dirty_with_soil_outside')")
            c.execute("INSERT into DETAILS values(26,'dirty_with_soil_inside')")
            c.execute("INSERT into DETAILS values(27,'water_in_bottle')")
            c.execute("INSERT into DETAILS values(28,'dirty_outside')")
            c.execute("INSERT into DETAILS values(29,'closed_cap_bottles')")
            c.execute("INSERT into DETAILS values(30,'broken_side')")
            c.execute("INSERT into DETAILS values(31,'broken_under')")
            c.execute("INSERT into DETAILS values(32,'broken_inside')")
            c.execute("INSERT into DETAILS values(33,'broken_top')")
            c.execute("INSERT into DETAILS values(34,'chipped_finsidh_from_beer_factory')")
            c.execute("INSERT into DETAILS values(35,'shark_mouth')")
            c.execute("INSERT into DETAILS values(36,'scuff')")
            c.execute("INSERT into DETAILS values(37,'deep_scratch')")
            c.execute("INSERT into DETAILS values(38,'rainbow')")
            c.execute("INSERT into DETAILS values(39,'sprayed_or_painted')")
            c.execute("INSERT into DETAILS values(40,'termites')")
            c.execute("INSERT into DETAILS values(41,'wrong_label')")
            
            self.conn.commit()
        except:
            pass
        c.close()

    def query(self, queryString, bind=()):
        if(queryString.lower().find("select") == -1):
            return -1
        c = self.conn.cursor()
        rows = []
        for row in c.execute(queryString, bind):
            rows.append(row)
        c.close()
        return rows
    
    def modifyTable(self, queryString, binding_tuple):
        c = self.conn.cursor()
        c.execute(queryString, binding_tuple)
        returnVal =  c.lastrowid
        self.conn.commit()
        c.close()
        return returnVal
        
    

    def query_alltag(self):
        c = self.conn.cursor()
        query_alltags = []
        for row in c.execute("SELECT Tag_No, Description FROM DETAILS"):
            query_alltags.append(row[1])
        c.close()
        return query_alltags
    
    def query_alltag1(self):
        c = self.conn.cursor()
        query_alltags1 = []
        
        for row in c.execute("SELECT tag_name FROM Filter_tag "):
            query_alltags1.append(row[0])
        c.close()
        return query_alltags1

    def getAllFilter(self):
        c = self.conn.cursor()
        filter_tag = []
        for row in c.execute("SELECT * FROM Filter"):
            filter_tag.append(row)
        c.close()
        return filter_tag

    def createNewFilter(self, pipName,view, tag, description, trainable, performance=0, averageTime=0, ses=0):
        c = self.conn.cursor()
        c.execute("INSERT into Filter VALUES (?,?,?,?,?)", (pipName, tag, view, description, trainable))
        self.conn.commit()
        c.close()



if(__name__ == "__main__"):
    db = databaseManager()
    db.conn.close()