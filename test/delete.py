#!/usr/bin/python3

#
# Delete a single record
#

import httplib2
import sys


if len(sys.argv) != 2:
  print("Must supply a record number")
  sys.exit(1)

arg = int(sys.argv[1])
url = "http://10.2.7.85:8080/device/%d" % arg

h = httplib2.Http()
resp, content = h.request(url, "DELETE", None, headers={'Content-Type': 'application/json; charset=UTF-8', 'key': 'c8001d6e-247b-48c6-a1bc-105951002ae9'})
print("status = %s" % resp['status']);
