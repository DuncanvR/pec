## Imports
import os
from pysqlite2 import dbapi2 as sqlite3
import sys

## Constants
PEC_VERSION = '0.1'
DB_VERSION  = 1

## Defaults
DEFAULT_DB_FILE = "db.sqlite"

## Functions
def main():
   # Retrieve arguments
   try:
      opts, args = getopt.getopt(sys.argv[1:], "", [])
   except getopt.GetoptError as err:
      print str(err)
      usage()
      sys.exit(2)

   # Set default values

   # Process arguments

   # Start the program

def usage():
   print "Usage: " + sys.argv[0] + " [options]"
