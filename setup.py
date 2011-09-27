from distutils.core import setup

PKGLIST = ['gearman_geodis']
    

setup(name='gearman-geodis',
      version='1.0.0',
      description='Geolocation Gearman worker powered by Geodis',
      author_email='engineering@shazamteam.com',
      license='Apache License, Version 2.0',
      packages=PKGLIST,	
      scripts=['gearman_geodis/geodis_worker.py', 'gearman_geodis/gearman_geodisd.py', 'gearman_geodis/stdin_geodis_worker.py'],
      data_files=[('/etc/sysconfig/',['support/gearman_geodis.sysconfig']),
		  ('/etc/init.d/',['support/gearman_geodis'])]
	
      )
