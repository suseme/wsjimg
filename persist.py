__author__ = 'vin@misday.com'

from pyvin.core import SqliteHelp

# article
## id, title, content, date, url, download, read, deleted,
#  picture
## id, article_id, url, filename, description

# trigger
## delete picture items while deleting article.

class WsjPersist(SqliteHelp):
    DB_NAME = 'data.db'
    DB_VER = 2

    CREATE_ART_TBL = '''
    CREATE TABLE IF NOT EXISTS article (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        date TEXT NOT NULL,
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        download INTEGER NOT NULL DEFAULT 0,
        read INTEGER NOT NULL DEFAULT 0,
        deleted INTEGER NOT NULL DEFAULT 0
    );
    '''
    CREATE_PIC_TBL = '''
    CREATE TABLE IF NOT EXISTS picture
    (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        article_id INTEGER NOT NULL DEFAULT 0,
        url TEXT NOT NULL,
        src TEXT NOT NULL,
        alt TEXT NOT NULL,
        download INTEGER NOT NULL DEFAULT 0
    );
    '''

    def __init__(self):
        SqliteHelp.__init__(self, WsjPersist.DB_NAME, WsjPersist.DB_VER)

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    # overide
    def onCreate(self):
        self.cursor.execute(WsjPersist.CREATE_ART_TBL)
        self.cursor.execute(WsjPersist.CREATE_PIC_TBL)
        self.conn.commit()

    def addArt(self, url, date):
        query = 'SELECT url FROM article WHERE url = ?'
        self.cursor.execute(query, (url,))
        rows = self.cursor.fetchall()
        if len(rows) < 1:
            query = 'INSERT INTO article (\'url\', \'date\', \'title\', \'summary\') VALUES (?, ?, \'\', \'\')'
            self.cursor.execute(query, (url, date))
            self.conn.commit()
            return True
        else:
            return False

    def updateArt(self, url, title, summary):
        query = 'UPDATE article SET title = ?, summary = ? WHERE url = ?'
        # print url
        # print title
        # print summary
        self.cursor.execute(query, (url, title, summary))
        self.conn.commit()

    def setArtDownload(self, url):
        query = 'UPDATE article SET download = 1 WHERE url = ?'
        self.cursor.execute(query, (url,))
        self.conn.commit()

    def setArtRead(self, url):
        query = 'UPDATE article SET read = 1 WHERE url = ?'
        self.cursor.execute(query, (url,))
        self.conn.commit()

    def getArts(self):
        query = 'SELECT * FROM article'
        self.cursor.execute(query)
        values = self.cursor.fetchall()
        return values

    def getArtsUndownload(self):
        query = 'SELECT * FROM article WHERE download = 0'
        self.cursor.execute(query)
        values = self.cursor.fetchall()
        return values

    def getArtsByUrl(self, url):
        query = 'SELECT * FROM article WHERE url = ?'
        self.cursor.execute(query, (url,))
        values = self.cursor.fetchall()
        return values

    def getArtById(self, id):
        query = 'SELECT * FROM article WHERE id = ?'
        self.cursor.execute(query, (id, ))
        values = self.cursor.fetchall()
        return values

    def getArtIdByUrl(self, url):
        query = 'SELECT id FROM article WHERE url = ?'
        self.cursor.execute(query, (url, ))
        rows = self.cursor.fetchall()
        if len(rows) > 0:
            return rows[0][0]
        else:
            return 0

    def isArtDownload(self, url):
        query = 'SELECT download FROM article WHERE url = ?'
        self.cursor.execute(query, (url, ))
        rows = self.cursor.fetchall()
        if len(rows) > 0:
            down = rows[0][0]
            return down == 1
        else:
            return False

    #-------------------------------------------------------------------------------------------------------------------

    def addPic(self, article_id, url, src, alt):
        # print article_id
        # print url
        # print src
        # print alt
        query = 'SELECT url FROM picture WHERE url = ?'
        self.cursor.execute(query, (url,))
        rows = self.cursor.fetchall()
        if len(rows) < 1:
            query = 'INSERT INTO picture (\'article_id\', \'url\', \'src\', \'alt\') VALUES (?, ?, ?, ?)'
            self.cursor.execute(query, (article_id, url, src, alt))
            self.conn.commit()
            return True
        else:
            return False

    def setPicDownload(self, url):
        query = 'UPDATE picture SET download = 1 WHERE url = ?'
        self.cursor.execute(query, (url,))
        self.conn.commit()

    def getPics(self, article_id):
        query = 'SELECT * FROM picture WHERE article_id = ?'
        self.cursor.execute(query, (article_id, ))
        values = self.cursor.fetchall()
        return values

if __name__ == "__main__":
    print 'persist'
    persist = WsjPersist()
