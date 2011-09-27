#! /bin/python
'''
This is a gearman worker that resolves (latitude, longitude)
tuples to locations using the geodis library.

See usage in main function for more.
'''
import sys
import redis
import os
import traceback
import re
import signal

from gearman_geodis.GeodisWorker import BasicGeodisWorker

def main(argv=sys.argv):	

	usage = '''
	Usage:
	stdin_geodis_worker.py <redis_host:port:db> <gearman_host:port>

	redis_host:port:db: The redis instance and DB to connect to.
			Example:
				localhost:6379:9

	gearman_host:port: The gearman server to assign connect workers to.
			Example:
				myhost.com:4730

	'''

	if len(argv) != 3:
		print >> sys.stderr, "Requires 2 arguments"
		print >> sys.stderr, usage
		sys.exit(1)	

	res = re.match("^([^\:]+)\:(\d+)\:(\d+)$", argv[1])
	if not res:
		print >> sys.stderr, "Invalid Redis DB string"
		print >> sys.stderr, usage
		sys.exit(1)

	redisHost = res.group(1)
	redisPort = int(res.group(2))
	redisDb = int(res.group(3))

	res = re.match("^([^\:]+)\:(\d+)$", argv[2])
	if not res:
		print >> sys.stderr, "Invalid Gearman server string"
		print >> sys.stderr, usage
		sys.exit(1)

	redisClient = redis.Redis(host=redisHost, port=redisPort, db=redisDb)

	worker = BasicGeodisWorker(redisClient)

	while True:
		
		line = sys.stdin.readline()
		if not line:
			break
	
		print worker.lookup(line)
		
if __name__ == "__main__":
	sys.exit(main())

