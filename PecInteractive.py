## Imports
import PecMain
import cmd
import datetime
from pysqlite2 import dbapi2 as sqlite3
import subprocess

class PecInteractive(cmd.Cmd):
   prompt = "Pec > "

   def __init__(self, db_path):
      cmd.Cmd.__init__(self)
      self.db_path = db_path
      (self.db_connection, self.db_cursor) = PecMain.connect_db(db_path)

   def postloop(self):
      print

   def do_EOF(self, line):
      return True

   def do_shell(self, line):
      try:
         print subprocess.check_output(line, shell=True)
      except subprocess.CalledProcessError as err:
         raise Exception("Error while executing shell command: " + str(err))

   def do_add(self, line):
      """add cmd
      Adds the command to the database"""
      print "Adding the command: " + line
      try:
         self.db_cursor.execute('INSERT INTO pec_experiments (cmd) VALUES (?)', (line,))
         self.db_connection.commit()
      except sqlite3.OperationalError as err:
         raise Exception("Error while inserting command: " + str(err))

   def do_execute(self, line):
      """execute task_id
      Execute the task(s) with the given id(s).
      Multiple ids can be separated by comma's, and ranges can be specified with a dash."""
      for r in line.split(','):
         r = r.split('-')
         if len(r) == 1:
            r.append(r[0])
         for i in range(int(r[0]), int(r[1]) + 1):
            self.db_cursor.execute('SELECT cmd FROM pec_experiments WHERE id = ?', (i,))
            task = self.db_cursor.fetchone()
            if task == None:
               print "Unable to find task " + str(i)
            else:
               print "Executing task " + str(i) + ", running command: " + task[0]
               # Close the database connection
               self.db_cursor.close()
               self.db_connection.close()
               try:
                  # Run the command
                  ro = subprocess.check_output(task[0], shell=True)
               except subprocess.CalledProcessError as err:
                  print "   Error while running task " + str(i)
                  ro = err.output
               # Reopen the database connection
               (self.db_connection, self.db_cursor) = PecMain.connect_db(self.db_path)
               # Save the results
               self.db_cursor.execute('UPDATE pec_experiments SET date_run = ?, raw_output = ? WHERE id = ?', (datetime.datetime.now().ctime(), ro, i))
               self.db_connection.commit()

   def do_list(self, line):
      """list
      Lists the commands in the database"""
      print "\tCmd\t|\tDate run\t\t\t|\tOutput"
      self.db_cursor.execute('SELECT id, cmd, date_run, raw_output FROM pec_experiments')
      for (i, c, dr, ro) in self.db_cursor.fetchall():
         print str(i) + ":\t" + c + "\t|\t" + (dr or "never\t\t\t") + "\t|\t" + (ro or "")

   def do_remove(self, line):
      """remove task_id
      Removes the task(s) with the given id(s) from the database.
      Multiple ids can be separated by comma's, and ranges can be specified with a dash."""
      for r in line.split(','):
         r = r.split('-')
         if len(r) == 1:
            r.append(r[0])
         for i in range(int(r[0]), int(r[1]) + 1):
            print "Removing task " + str(i)
            self.db_cursor.execute('DELETE FROM pec_experiments WHERE id = ?', (i,))
      self.db_connection.commit()

   def do_reset(self, line):
      """reset task_id
      Reset the task(s) with the given id(s), clearing its running information.
      Multiple ids can be separated by comma's, and ranges can be specified with a dash."""
      for r in line.split(','):
         r = r.split('-')
         if len(r) == 1:
            r.append(r[0])
         for i in range(int(r[0]), int(r[1]) + 1):
            print "Resetting task " + str(i)
            self.db_cursor.execute('UPDATE pec_experiments SET date_run = NULL, raw_output = NULL WHERE id = ?', (i,))
      self.db_connection.commit()
