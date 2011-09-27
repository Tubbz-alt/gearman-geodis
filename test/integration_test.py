#! /usr/bin/python

'''
This test starts a worker and client. The client makes 
1k random calls via gearman.

There must be a local gearmand and redis instance.
'''

import sys
import time
sys.path.append("../gearman_geodis") 
#from GeodisWorker import GeodisWorker
#from WorkerThread import WorkerThread
import gearman
import random
import redis
import json
import os
from geodis.provider.geonames import GeonamesImporter
from geodis.provider.ip2location import IP2LocationImporter
from geodis.provider.zipcodes import ZIPImporter
import geodis
from threading import Thread

scriptDir = os.path.dirname(__file__)

if len(sys.argv) < 4:
	print "Usage: <client count> <worker count> <request count per client>"
	sys.exit(-1)

clientCount = int(sys.argv[1])
workerCount = int(sys.argv[2])
numReqs = int(sys.argv[3])

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


def check_request_status(job_request):
    assert job_request.complete
    assert 'city' in json.loads(job_request.result)

class ClientThread(Thread):

	def __init__(self, reqCnt):
		Thread.__init__(self)
		self.reqCnt = reqCnt
		self.gm_client = gearman.GearmanClient(['localhost:4730'])
		

	def run(self):
		for _ in xrange(0,numReqs):
		        lat = 90.0 - (180.0 * random.random())
        		lon = 180.0 - (360.0 * random.random())

        		job_request = self.gm_client.submit_job("geodis_lookup_city", "%f,%f" % (lat,lon))
        		check_request_status(job_request)


redisHost='localhost'
redisPort=6379
redisDb=9

redisClient = redis.Redis(host=redisHost, port=redisPort, db=redisDb)


# Test if data loading is required
if geodis.City.getByLatLon(0.0,0.0, redisClient) is None:
	initDb(redisHost, redisPort, redisDb)

'''
if 0 != os.fork():


	for n in range(workerCount):
		worker = WorkerThread(GeodisWorker(redisClient, 'localhost:4730'))
		worker.start()
'''

time.sleep(1)
print "Starting clients"
clients = [ClientThread(numReqs) for _ in range(clientCount)]

start = time.time()
for c in clients:
	c.start()
for c in clients:
	c.join()
	
total = time.time() - start
totalReqs = numReqs * clientCount
print "%f requests took %f sec, req / sec = %f, sec / req = %f" % (numReqs, total, float(totalReqs) / float(total), total / totalReqs)

