## Imports
import PecInteractive
import PecRunner
import getopt
import os
from pysqlite2 import dbapi2 as sqlite3
import sys

## Constants
PEC_VERSION      = '0.1'
DB_VERSION       = '1'
MODE_INTERACTIVE = 6000
MODE_RUNNER      = 6001

## Defaults
DEFAULT_DB_FILE = "db.sqlite"
DEFAULT_MODE    = MODE_INTERACTIVE

## Functions
def connect_db(db_path):
   db_connection = sqlite3.connect(db_path)
   db_cursor = db_connection.cursor()
   # Check database version
   try:
      db_cursor.execute('SELECT value FROM pec_meta WHERE name = "db_version"')
   except sqlite3.OperationalError:
      create_db(db_connection, db_cursor)
   else:
      version = db_cursor.fetchone()[0]
      if version != DB_VERSION:
         raise Exception("Wrong database version")
   return (db_connection, db_cursor)

def create_db(db_connection, db_cursor):
   try:
      db_cursor.execute('CREATE TABLE pec_meta  ( name  VARCHAR(30) PRIMARY KEY  ' \
                                               ', value TEXT                    )' )
      db_cursor.execute('INSERT INTO  pec_meta SELECT "db_version" AS name, ? AS value' ,
                        (DB_VERSION)                                                    )
      db_cursor.execute('CREATE TABLE pec_experiments ( id         INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT ' \
                                                     ', cmd        TEXT     NOT NULL                           ' \
                                                     ', date_run   DATETIME                                    ' \
                                                     ', raw_output TEXT                                       )' )
      db_connection.commit()
   except sqlite3.OperationalError as err:
      raise Exception("Error while creating tables: " + str(err))


def main():
   # Retrieve arguments
   try:
      opts, args = getopt.getopt(sys.argv[1:], "d:hr", ["database=", "help", "runner"])
   except getopt.GetoptError as err:
      print str(err)
      usage()
      sys.exit(2)

   # Set default values
   db_path = DEFAULT_DB_FILE
   mode    = DEFAULT_MODE

   # Process arguments
   for o, a in opts:
      if o in ("-d", "--database"):
         db_path = a
      elif o in ("-h", "--help"):
         usage()
         sys.exit()
      elif o in ("-r", "--runner"):
         mode = MODE_RUNNER

   db = connect_db(db_path)

   # Start the program
   if   mode == MODE_INTERACTIVE:
      PecInteractive.PecInteractive(db).cmdloop()
   elif mode == MODE_RUNNER:
      PecRunner.PecRunner(db).run()
   else:
      raise Exception("Unknown mode " + str(mode))

def usage():
   print "Usage: " + sys.argv[0] + " [options]"
   print "Options:"
   print "   --database=file   The database file to use, default is " + DEFAULT_DB_FILE + " in the working directory"
   print "   --help            Shows this help message"
   print "   --runner          Starts the daemon running the experiments"
   print "Each long option --opt also has a short version -o"
