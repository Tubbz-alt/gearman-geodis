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

from gearman_geodis.GeodisWorker import GeodisWorker
from gearman_geodis.WorkerThread import WorkerThread

from geodis.provider.geonames import GeonamesImporter
from geodis.provider.ip2location import IP2LocationImporter
from geodis.provider.zipcodes import ZIPImporter
import geodis

workers = []	
doWork = True

 
def main(argv=sys.argv):	

	global workers
	global doWork

	usage = '''
	Usage:
	geodis_worker.py <worker_count> <redis_host:port:db> <gearman_host:port>

	worker_count: integer greater than 0. The number of threaded 
			workers to create.
	redis_host:port:db: The redis instance and DB to connect to.
			Example:
				localhost:6379:9

	gearman_host:port: The gearman server to assign connect workers to.
			Example:
				myhost.com:4730

	'''

	if len(argv) != 4:
		print >> sys.stderr, "Requires 3 arguments"
		print >> sys.stderr, usage
		sys.exit(1)	

	workerCount = int(argv[1])

	res = re.match("^([^\:]+)\:(\d+)\:(\d+)$", argv[2])
	if not res:
		print >> sys.stderr, "Invalid Redis DB string"
		print >> sys.stderr, usage
		sys.exit(1)

	redisHost = res.group(1)
	redisPort = int(res.group(2))
	redisDb = int(res.group(3))

	res = re.match("^([^\:]+)\:(\d+)$", argv[3])
	if not res:
		print >> sys.stderr, "Invalid Gearman server string"
		print >> sys.stderr, usage
		sys.exit(1)

	gmHostPort = res.group(0)

	redisClient = redis.Redis(host=redisHost, port=redisPort, db=redisDb)

	# Test if data loading is required
	if geodis.City.getByLatLon(0.0,0.0, redisClient) is None:
		initDb(redisHost, redisPort, redisDb)

	""" Start worker threads which will be stopped by SIGTERM """
	for i in range(workerCount):
		print "Starting worker thread %d" % i
		worker = WorkerThread(GeodisWorker(redisClient, gmHostPort))
		workers.append(worker)
		worker.start()

	while doWork:
		pass
		

def handle_sigterm(sig, func=None):
	""" Shutdown gracefully by stopping all worker threads """
	global doWork

	print "Stopping worker daemon"
	doWork = False

signal.signal(signal.SIGTERM, handle_sigterm)
	
def initDb(redisHost, redisPort, redisDb):
	'''
	Load geodis packaged city data into the redis DB
	'''
		
	print "Initializing Redis data"

	try:
		scriptDir = os.path.dirname(__file__)
		zipFile = "/opt/geodis/data/zipcode.csv"
		importer = ZIPImporter(zipFile, redisHost, redisPort, redisDb)
		
		if not importer.runImport():
			print >> sys.stderr, "Could not import geonames database..."
			sys.exit(1)
		
		cityFile = "/opt/geodis/data/cities1000.txt"
		adminFile = "/opt/geodis/data/admin1Codes.txt"
		importer = GeonamesImporter(",".join([cityFile, adminFile]), redisHost, redisPort, redisDb)
		
		if not importer.runImport():
			print >> sys.stderr, "Could not import geonames database..."
			sys.exit(1)
			
	except:
		traceback.print_exc(file=sys.stderr)
		sys.exit(1)
		
		
if __name__ == "__main__":
    sys.exit(main())

