## Imports
import PecMain
from pysqlite2 import dbapi2 as sqlite3
import subprocess
import threading

class PecRunner:
   def __init__(self, db_path, executable):
      self.db_path = db_path
      self.executable = executable

   def start_daemon(self):
      print "Project Experiment Controller v" + PecMain.PEC_VERSION
      (db_connection, db_cursor) = PecMain.connect_db(self.db_path)
      db_cursor.execute('SELECT value FROM pec_meta WHERE name = "thread_count"')
      thread_count = int(db_cursor.fetchone()[0])
      db_cursor.close()
      db_connection.close()
      # Start threads
      for i in xrange(thread_count):
         PecRunnerThread(self.db_path, self.executable).start()

class PecRunnerThread(threading.Thread):
   def __init__(self, db_path, executable):
      threading.Thread.__init__(self)
      self.db_path = db_path
      self.executable = executable

   def run(self):
      while True:
         # Open the database connection
         (db_connection, db_cursor) = PecMain.connect_db(self.db_path)
         # Retrieve a task
         db_cursor.execute('UPDATE pec_experiments SET raw_output = ? WHERE id = (SELECT id FROM pec_experiments WHERE date_run IS NULL AND raw_output IS NULL LIMIT 1)', (self.name,))
         db_connection.commit()
         db_cursor.execute('SELECT id FROM pec_experiments WHERE raw_output = ?', (self.name,))
         task = db_cursor.fetchone()
         # Close database connection
         db_cursor.close()
         db_connection.close()

         # Stop when no more tasks are available
         if task == None:
            break
         # Execute the task
         subprocess.call([self.executable, "-c", "execute " + str(task[0])])
