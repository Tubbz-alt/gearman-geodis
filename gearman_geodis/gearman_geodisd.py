#! /bin/python
import sys, time
from gearman_geodis.daemon import Daemon
import gearman_geodis.geodis_worker 

class GearmanGeodisDaemon(Daemon):
	'''
	Daemon wrapper around geodis_worker.py
	'''

	def run(self):
		global workerArgs
		gearman_geodis.geodis_worker.main(workerArgs)
 
if __name__ == "__main__":
	pidFile = sys.argv[1]
	workerArgs = ["geodis_worker.py"]
	workerArgs.extend(sys.argv[3:])
        daemon = GearmanGeodisDaemon(pidFile, 
			stdout='/var/log/gearman_geodis/gearman_geodis.out',
			stderr='/var/log/gearman_geodis/gearman_geodis.err')
        if len(sys.argv) >= 3:
                if 'start' == sys.argv[2]:
                        daemon.start()
                elif 'stop' == sys.argv[2]:
                        daemon.stop()
                elif 'restart' == sys.argv[2]:
                        daemon.restart()
                else:
                        print "Unknown command"
                        sys.exit(2)
                sys.exit(0)
        else:
                print "usage: %s <pid_file> start|stop|restart <geodis_worker_options>" % sys.argv[0]
                sys.exit(2)
