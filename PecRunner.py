## Imports
import datetime
import os
from pysqlite2 import dbapi2 as sqlite3
import sys

class PecRunner:
   def __init__(self, db):
      (self.db_connection, self.db_cursor) = db

   def run(self):
      print "Pec - Running all new commands"
      self.db_cursor.execute('SELECT id, cmd FROM pec_experiments WHERE date_run IS NULL')
      for (i, c) in self.db_cursor.fetchall():
         print "\tRunning command: " + c
         ro = os.popen(c).read()
         print "\t\tOutput:"
         print ro
         self.db_cursor.execute('UPDATE pec_experiments SET date_run = ?, raw_output = ? WHERE id = ?', (datetime.datetime.now().ctime(), ro, i))
         self.db_connection.commit()
