Gearman Geodis
==============

This package is a *thin* Python wrapper which exposes Geodis' 
geolocation lookup functionality as a Gearman worker.
The main executable, gearman_worker.py, creates a single threaded worker.
The associated 'gearman_geodis' service, that is installed with the optional RPM,
creates a process based worker pool. The number of processes in the worker 
pool is controlled by the gearman_geodis.sysconfig file.

Gearman: http://gearman.org

Geodis: https://github.com/doat/geodis

The associated RPM package installs the service 'gearman_geodis'.

The gearman_geodis service runs as user gearman_geodis.

Gearman Protocol
----------------
The worker(s) resolves provided geographic coordinates (latitude and longitude) to closest location. 
The lookup service is provided by the geodis library using default data set.
        
The Gearman request body must be a string of format of: 
	'<lat>,<lon>',
where lat and lon are ASCII string representations of float.
        
The job response upon successful lookup is a JSON string of format:

`{'city': '<city>', 'zip': '<zip>', 'country': '<country>', 'lat': '<lat>', 'lon': '<lon>', 'state': '<state>'}`
       
Fields:

+ **city** - City name
+ **zip** - ZIP code (optional)
+ **country** - Country
+ **lat** - Latitude
+ **lon** - Longitude
+ **state** - State (optional)

The zip and state fields only appear for locations within the United States.
        
An error response is a JSON string of format:
        `{'error':'<error>'}`
        
Where error is a string description.


Dependencies (Build / Test / Running)
-------------------------------------
+ **geodis** https://github.com/doat/geodis
+ **geohasher** http://pypi.python.org/pypi/geohasher
+ **python-gearman** http://pypi.python.org/pypi/gearman/
+ **redis-py** https://github.com/andymccurdy/redis-py


Building
--------
You may package and install using distutils (setup.py).

If you to use gearman-geodis as a service, there are scripts and configuration files to build an RPM which will install the service.
To build the RPM, first ensure rpm-build is installed.

$ ./build_rpm

The RPM will be in the ./dist directory.

Testing
-------
Ensure Gearman and Redis are running.

$ ./run_test

Configuration
-------------

The service configuration file is:
        /etc/sysconfig/gearman_geodis.sysconfig

By default, the worker registers with a local gearmand and
uses a local redis instance. The default ports are used for
both redis and gearmand.

Running
-------

To start the service:
	$ service gearmand_geodis start

The gearman_geodis service runs as user gearman_geodis.

The log files are found at:
	/var/log/gearman_geodis/
The pid files are found in:
	/var/log/gearman_geodis/
The service configuration file is:
	/etc/sysconfig/gearman_geodis.sysconfig
	
Copyright and License
---------------------

Copyright 2011 Shazam Entertainment Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this work except in compliance with the License.
You may obtain a copy of the License in the LICENSE file, or at:

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

