
from threading import Thread
import traceback
import sys

class WorkerThread(Thread):
    '''
    A simple thread wrapper around a worker.
    When running, any exception thrown by the working is logged to stderr and the worker is 
    logged and the worker restarted.
    '''
    
    def __init__(self, worker):
        
        Thread.__init__(self)
	
        self.worker = worker
	self.daemon = True

    def run(self):
        while True:
            try:
                self.worker.work()
            except:
		print >> sys.stderr, "Caught exception: "
                traceback.print_exc(file=sys.stderr)
		print >> sys.stderr, "Restarting worker"
                
        
        
