'''
GeodisWorker

Implements Gearman worker with geo-lookup job logic provided by geodis.

See method 'lookup' for more details.
'''
import sys
import traceback
import gearman
import json

import geodis
from geodis.zipcode import ZIPCode

class BasicGeodisWorker(object):
    
    def __init__(self, redisClient):
        
        self.redisClient = redisClient
        
    @classmethod
    def hasZIPCodeData(cls, country):
        '''
        Default geodis data set only provide zipcode data for US.
        '''
        return country == 'United States' 
        
    def lookup(self, req):
        '''
        Handles a Gearman string req. 
        Method interface required by python-gearman
        
        Resolves provided geographic coordinates to closest location. 
        The lookup service is provided by the geodis library and default data set.
        
        req should be a string of format of '<lat>,<lon>' format,
        where lat and lon are ASCII string representations of float.
        
        The job response upon successful lookup is a JSON string of format:
        {'city': '<city>', 'zip': '<zip>', 'country': '<country>', 
        'lat': '<lat>', 'lon': '<lon>', 'state': '<state>'}
        
        Fields:
        city - City name.
        zip - ZIP code (optional)
        country - Country
        lat - Latitude of found location
        lon - Longitude of found location
        state - State (optional)
        
        An error response is a JSON string of format:
        {'error':'<error>'}
        where error is a string description.
        '''
                
        lat, lon = req.split(",")
        lat = float(lat)
        lon = float(lon)

        try:
            loc = geodis.City.getByLatLon(lat, lon, self.redisClient)
            
            if self.hasZIPCodeData(loc.country):
                '''
                We only lookup location's zip after determining it 
                is in a supported country. Otherwise, geodis' ZIPCode
                lookup will return a location within a country that has a
                zip code. So a lookup for zip in unsupported UK would 
                return a ZIP somewhere in Maine, US.
                '''
                loc = ZIPCode.getByLatLon(lat, lon, self.redisClient)
                resp = formatZipResponse(loc)
            else:
                resp = formatCityResponse(loc)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            traceback.print_exc()
            resp = formatErrResponse(str(sys.exc_info()[0]))    

        return resp    
        

class GeodisWorker(BasicGeodisWorker):
    '''
    A GeodisWorker with and Gearman server handle.
    '''
    
    def __init__(self, redisClient, gearmanHost):
        
        BasicGeodisWorker.__init__(self, redisClient)
        
        self.worker = gearman.GearmanWorker([gearmanHost])
        
        self.worker.register_task('geodis_lookup_city', self.lookup)
        print "Registered worker"
        
    def lookup(self, worker, job):
        ''' worker arg is unused but required in Gearman callback '''
        return BasicGeodisWorker.lookup(self, job.data)
        
    def work(self):
        self.worker.work()


def formatErrResponse(errMsg):
    return json.dumps({'error':str(errMsg)})

def formatCityResponse(loc):
    return json.dumps({'city':loc.name, 'zip':'', 'country': loc.country,
                       'lat':loc.lat, 'lon':loc.lon, 'state':loc.state})

def formatZipResponse(loc):
    return json.dumps({'city':loc.city, 'zip':loc.name, 'country': loc.country,
                       'lat':loc.lat, 'lon':loc.lon, 'state':loc.state})
