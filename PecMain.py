# Pec - Program entry point
# Copyright (C) 2012-2013 DJ van Roermund
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

## Imports
import PecInteractive
import PecRunner
import getopt
from pysqlite2 import dbapi2 as sqlite3
import sys

## Constants
PEC_VERSION      = '0.2'
DB_VERSION       = '1'
MODE_CLI         = 6000
MODE_INTERACTIVE = 6001
MODE_RUNNER      = 6002

## Defaults
DEFAULT_DB_FILE      = "./db.sqlite"
DEFAULT_MODE         = MODE_INTERACTIVE
DEFAULT_THREAD_COUNT = 2

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
      db_cursor.execute('INSERT INTO  pec_meta SELECT "db_version" AS name, ? AS value' \
                                       ' UNION SELECT "thread_count",       ?'          ,
                        (DB_VERSION, DEFAULT_THREAD_COUNT)                              )
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
      opts, args = getopt.getopt(sys.argv[1:], "c:d:hr", ["cli=", "database=", "help", "runner"])
   except getopt.GetoptError as err:
      print str(err)
      usage()
      sys.exit(2)

   # Set default values
   db_path = DEFAULT_DB_FILE
   mode    = DEFAULT_MODE

   # Process arguments
   for o, a in opts:
      if o in ("-c", "--cli"):
         mode = MODE_CLI
         cli = a
      elif o in ("-d", "--database"):
         db_path = a
      elif o in ("-h", "--help"):
         usage()
         sys.exit()
      elif o in ("-r", "--runner"):
         mode = MODE_RUNNER

   # Start the program
   if mode == MODE_CLI:
      PecInteractive.PecInteractive(db_path).onecmd(cli)
   elif mode == MODE_INTERACTIVE:
      PecInteractive.PecInteractive(db_path).cmdloop()
   elif mode == MODE_RUNNER:
      PecRunner.PecRunner(db_path, sys.argv[0]).start_daemon()
   else:
      raise Exception("Unknown mode " + str(mode))

def usage():
   print "Project Experiment Controller v" + PEC_VERSION
   print "Usage: " + sys.argv[0] + " [options]"
   print "Options:"
   print "   --cli=cmd         Passes the given command to the interactive command interpreter and exits"
   print "   --database=file   The database file to use, default is " + DEFAULT_DB_FILE
   print "   --help            Shows this help message"
   print "   --runner          Starts the daemon running the experiments"
   print "Each long option --opt also has a short version -o"
