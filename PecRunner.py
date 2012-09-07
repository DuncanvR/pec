## Imports
import PecMain
import datetime
import os
from pysqlite2 import dbapi2 as sqlite3
import Queue
import threading

class PecRunner:
   def __init__(self, db_path):
      self.db_path = db_path
      (self.db_connection, self.db_cursor) = PecMain.connect_db(db_path)

   def start_daemon(self):
      print "Pec - Running all new commands"

      # Retrieve tasks
      tasks = Queue.Queue(0)
      self.db_cursor.execute('SELECT id, cmd FROM pec_experiments WHERE date_run IS NULL')
      for (i, c) in self.db_cursor.fetchall():
         tasks.put((i, c))

      # Start threads
      self.db_cursor.execute('SELECT value FROM pec_meta WHERE name = "thread_count"')
      thread_count = int(self.db_cursor.fetchone()[0])
      for i in xrange(thread_count):
         PecRunnerThread(self.db_path, tasks).start()

class PecRunnerThread(threading.Thread):
   def __init__(self, db_path, tasks):
      threading.Thread.__init__(self)
      self.db_path = db_path
      self.tasks = tasks

   def run(self):
      # Open database connection
      (db_connection, db_cursor) = PecMain.connect_db(self.db_path)

      while not self.tasks.empty():
         # Retrieve a task
         task = self.tasks.get()
         if task != None:
            print "      Running command: " + task[1]
            ro = os.popen(task[1]).read()
            db_cursor.execute('UPDATE pec_experiments SET date_run = ?, raw_output = ? WHERE id = ?', (datetime.datetime.now().ctime(), ro, task[0]))
            db_connection.commit()

      # Close database connection
      db_cursor.close()
      db_connection.close()

