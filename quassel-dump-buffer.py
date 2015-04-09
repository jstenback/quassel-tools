#!/usr/bin/env python2

import psycopg2
from optparse import OptionParser
import sys

parser = OptionParser()
usage = "usage: %prog [options] arg1..."

parser.add_option("-u", "--user", type="string",
                  help="Quassel user",
                  dest="user", default=None)
parser.add_option("-n", "--network", type="string",
                  help="Quassel network", 
                  dest="network", default=None)
parser.add_option("-b", "--buffer", type="string",
                  help="Quassel buffer", 
                  dest="buffer", default=None)

options, arguments = parser.parse_args()

if options.user is None:
    print("user (--user) not specified, aborting.")

    sys.exit(1)

if options.network is None:
    print("network (--network) not specified, aborting.")

    sys.exit(1)

if options.buffer is None:
    print("buffer (--buffer) not specified, aborting.")

    sys.exit(1)

if len(arguments) != 0:
    print("Unknown arguments: {}".format(str(arguments)))

    sys.exit(1)

# Connect to the db
conn = psycopg2.connect("dbname=quassel")

cur = conn.cursor()

# Execute our statement
cur.execute('''SELECT time,sender,message,type FROM backlog
  INNER JOIN sender ON (backlog.senderid = sender.senderid)
  INNER JOIN buffer ON (backlog.bufferid = buffer.bufferid)
  INNER JOIN network ON (buffer.networkid = network.networkid)
  INNER JOIN quasseluser ON (buffer.userid = quasseluser.userid)
  WHERE username='{}' AND
        networkname='{}' AND
        buffername='{}'
  ORDER BY time;'''.format(options.user, options.network, options.buffer))

def time_str(t):
    return t.strftime("%H:%M:%S")

last_date = None

# Walk over the results.
for row in cur:
    if row[3] != 1:
        continue

    t = row[0]

    if t.date() != last_date:
        print("\n - {{Day change, {}}}".format(t.strftime("%A %B %m %Y, %Y-%m-%d")))

        last_date = t.date()

    print("{} |{:10s}|{}".format(time_str(row[0]), row[1].split('!')[0][:10], row[2]))
