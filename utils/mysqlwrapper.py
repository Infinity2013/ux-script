import MySQLdb
import os

def addquote(s):
    if isinstance(s, basestring):
        return "\"%s\"" % s
    else:
        return str(s)

class MySQLdbWrapper():

    def __init__(self):
        conn = MySQLdb.connect(host='localhost', user='root', passwd='1', port=3306)
        cur = conn.cursor()
        conn.select_db("ux")
        self.cur = cur
        self.conn = conn

    def insert(self, table, kargs):
        cmd = "insert into %s (%s) values(%s)" % (table, ", ".join(kargs.keys()), ", ".join(map(addquote, kargs.values())))
        self.cur.execute(cmd)
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()

    def dump(self, table):
        fd = open("%s/Documents/%s.csv" % (os.environ.get("HOME"), table), "w")
        cmd = "select * from %s" % table
        self.cur.execute(cmd)
        records = self.cur.fetchall()
        for r in records:
            fd.write(",".join(map(str, r[1:])))
            fd.write("\n")
        fd.close()


wrapper = MySQLdbWrapper()
