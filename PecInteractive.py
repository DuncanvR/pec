## Imports
import cmd
import os
from pysqlite2 import dbapi2 as sqlite3
import sys

class PecInteractive(cmd.Cmd):
   prompt = "Pec > "

   def __init__(self, db):
      cmd.Cmd.__init__(self)
      (self.db_connection, self.db_cursor) = db

   def postloop(self):
      print

   def do_EOF(self, line):
      return True

   def do_shell(self, line):
      print os.popen(line).read()

   def do_add(self, line):
      """add cmd
      Adds the command to the database"""
      print "Adding the command: " + line
      try:
         self.db_cursor.execute('INSERT INTO pec_experiments (cmd) VALUES (?)', (line,))
         self.db_connection.commit()
      except sqlite3.OperationalError as err:
         raise Exception("Error while inserting command: " + str(err))

   def do_list(self, line):
      print "\tCmd\t|\tDate run\t\t\t|\tOutput"
      self.db_cursor.execute('SELECT id, cmd, date_run, raw_output FROM pec_experiments')
      for (i, c, dr, ro) in self.db_cursor.fetchall():
         print str(i) + ":\t" + c + "\t|\t" + (dr or "never\t\t\t") + "\t|\t" + (ro or "")

   def do_remove(self, line):
      """remove task_id
      Removes the task with the given id.
      Multiple ids can be separated by comma's, and ranges can be specified as well."""
      for r in line.split(','):
         r = r.split('-')
         if len(r) == 1:
            r.append(r[0])
         for i in range(int(r[0]), int(r[1]) + 1):
            print "Removing task " + str(i)
            self.db_cursor.execute('DELETE FROM pec_experiments WHERE id = ?', (i,))
      self.db_connection.commit()

