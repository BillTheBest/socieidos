# Socieidos
A collection of micro-services that actively watches multiple social media mediums for specific media and retains this data for real-time consumption and analytics use cases.



Summary
=======
There are a range of social media platforms that exist today that are very popular to different types of users.  The information and interaction these platforms expose can be very valuabl to anyone who can properly store and consume the information.

**Socieidos** will have micro-services that connect to social media platforms through public APIs perform a DVR or keep a photographic memory with relevant metadata for objects that are available.  It will then expose a common API through distributed micro-services allowing a consumer to use this information.

Parameters
==========
The following parameters can be configured by either the ```/config/custom_config.py``` file or environment variables.  The environment variables will take priority.


	# REQUIRED
	s3_host = 'ip_or_fqdn'
	s3_akia = 'wuser1@sanity.local'
	s3_secret = 'lDcxQF/ez1yAeIQhz3AqglUyUydqdy5l+fK+4x1v'
	s3_bucket_name = 'social'
	s3_store_in = 'selfie'


	twitter_keys = "['key1','key2','key3','key4']"
	twitter_filter = "{'track':'selfie'}"

	# OPTIONAL
	s3_port = 10101
	s3_connect = "boto.connect_s3(lc_s3_akia,lc_s3_secret,is_secure=False,host=lc_s3_host,port=lc_s3_port,calling_format=OrdinaryCallingFormat())"
	s3_store = 'True'
	s3_object_expiration_time = 'timedelta(days=1)'
	s3_object_url_timeout = 1200
	s3_object_max_age = 3600
	job_s3_interval_delete_old_objects_minutes = 1
	min_items = 50

	get_objects_query_cache_seconds = 5

	twitter_request = 'statuses/filter'
	geo_box_coords_long_lat = '-125,24,-14,83'
	check_geo_coords = 'True'
	check_retweeted_status = 'True'
	check_possibly_sensitive = 'True'

	template_package_url = 'http://youpackage.tar.gz'
	template_file = 'default-us.html.template'
	template_param = """{
        'page_title': 'EMC CODE - Project Socieidos',
        'page_header1': 'EMC CODE',
        'carousel_image_first': '',
        'carousel_image_last': '',
        'page_footer':  \"\"\" 
                        \"\"\",
        'author_text':  \"\"\"
                        <p><strong>project socieidos</strong><br>
                        <a href="http://emccode.github.io">emccode.github.io</a></p>\"\"\" }"""


### Definitions

	### REQUIRED
	s3_host = The FQDN or IP of the s3 interface
	s3_akia = The s3 access key
	s3_secret = The s3 secret key
	s3_bucket_name = The s3 bucket_name
	s3_store_in = The directory to store objects in, ie. the s3://bucket_name/s3_store_in


	twitter_keys = The Twitter credentials
	twitter_filter = The filter based on the Python Twitter API implementation

	### OPTIONAL
	s3_port = The s3 port
	s3_connect = The s3 connection string based on the Python Twitter API implementation
	s3_store = Whether to actually store data or not (whatif)
	s3_object_expiration_time = An expression for the amount of expiration time an object has once it is written
	s3_object_url_timeout = The timeout that URLs that are generated for s3 objects have
	s3_object_max_age = The maximum time an object should exist before being manually deleted
	job_s3_interval_delete_old_objects_minutes = How often the delete job is ran
	min_items = The minimum number of objects to keep around

	get_objects_query_cache_seconds = The amount of seconds to wait before re-querying for the current list of objects

	twitter_request = The Twitter API specific filter
	geo_box_coords_long_lat = Geographic coordinates listed as SW_longitude,SW_latitude,NE_longitude,NE_latitide
	check_geo_coords = Whether to decide on processing by checking the coorindates
	check_retweeted_status = Whether to decide on processing by checking if retweet
	check_possibly_sensitive = Whether to decide on processing by checking if sensitive material flag is True
	lc_template_package_url = The URL where the .tar.gz package exists to be downloaded and uncompressed into /app
	template_file = The file that does or will exist at /app/templates to be rendered in response to HTTP requests to /
	template_param = The parameters that will be passed to the default.html.template file or template_file.

Configuration
=============
There are two ways to configure the ```TwitterCord``` container.

### Environment Variables
By running the docker container with ```-e``` parameters, you can specify configuration interactively with the parameter names as listed above and setting.

### Local file custom_config.py
You can also run the Docker container with a ```-v $(pwd):/config``` parameter (considering the config directory mounts) and if there is a ```custom_config.py``` file, all the values there will override configurable parameters.  If you run into issues with this method, mount the volume and use ```--entry-point=/bin/bash``` to run the container without starting the service.  From there look in the ```/config``` directory and run service manually with ```python TwitterCord.py```.


Running
=======
```Socieidos``` currently is able to monitor and record pictures from the Twitter API.  The Docker container is named ```emccode/twittercord```.
The following is a Docker command that will run the service with the specified parameters.  

Configuring with a static configuration file can be done by running ```docker run -ti -p 80:8080 -v $(pwd):/config emccode/twittercord``` where you specify a mount of the local directory to ```/config``` where a ```customer_config.py``` file exists.  Environment variables can still be used to override.


Configuring with environment variables takes priority over the items configured in a file.
```docker run -ti -p 80:8080 -e s3_host='ip_or_fqdn' -e s3_port='10101' -e s3_akia='wuser1@sanity.local' -e s3_secret='secret' -e s3_bucket_name=social -e s3_store_in=selfie -e twitter_keys="['app_key1','app_key2','user_key1','user_key2']" -e twitter_filter="{'track':'selfie'}" -e check_geo_coords='True' -e check_retweeted_status='True' -e check_possibly_sensitive='True' -e geo_box_coords_long_lat='-125,24,-14,83' -e s3_connect="boto.connect_s3(lc_s3_akia,lc_s3_secret,is_secure=False,host=lc_s3_host,port=lc_s3_port,calling_format=OrdinaryCallingFormat())" emccode/twittercord```


Presentation
============
Included is a default HTML page with a carousel to view images.  This is available from ```/```.  The page that is being rendered comes from ```/templates/default.html.template```.

### Static File
If you would like to modify the page, then you can do so by placing the iterative portion that declares the image tags wherever you please and in whatever format.  This could require that you build another version of ```TwitterCord``` that includes your static files.

	{% for object in objects %}
	<li><img src="{{ object['object_url'] }}"></li>
	{% endfor %}


### Template\_Param
There is an option to specify a ```template_param``` environment variable by adding it to your ```costom_config.py``` file as follows.  The parameters listed are used within the ```default.html.template``` file.  See this file to verify what the parameters fill in.  

	template_param = {
	        'page_title': 'EMC CODE - Project Socieidos',
	        'page_header1': 'EMC CODE',
	        'carousel_image_first': "",
	        'carousel_image_last': "",
	        'page_footer':  """ 
	                        """,
	        'author_text':  """
	                        <p><strong>project socieidos</strong><br>
	                        <a href="http://emccode.github.io">emccode.github.io</a></p>"""
	}

### Template\_Package\_Url
The most flexible and dynamic method would be to leverage this option.  Here you an specify the ```template_package_url``` parameter.  Upon application startup it will download a ```.tar.gz.``` file from this location and extract it, overwriting the files under ```/app```.  The file should include the following but is not limited in this way.  It does require that you locate files under directories to be compatible with ```Python Flask```.

	/templates/default.html-custom.template
	/static/*
	
### Template\_Package\_Url and Template\_Param
The combination of these two methods will yield the ultimate flexibility and dynamicness.
	
### Creating a Package
The following command will create a package that contains the correct directory structure.
```tar -zcvf package.tar.gz templates/default.html.template static/```


API
===
If you are interested in operating this in more of a micro-service architecture, there is a simple API available to expose the objects that are stored.  You can call ```GET /v1/objects``` to get a response as a ```JSON``` object.  This would allow you to use a carousel that leveraged AJAX or some active form of requesting images without refreshing a page.

## Get Objects
```GET /v1/objects```  

OK 200

	   {
			response = {
				requested_objects = ['tracker_name']
				objects[
					{
						object_url = "http://img.png",
						type = "image",
						source = "twitter",
						metadata = {
							text = "blah"
							screen_name = "blah"
							geo = [lat.0,long.0]
						}
					}
				]
			}
		}

## Docker Build
	git clone https://github.com/emccode/socieidos
	cd socieidos/Docker-twittercord
	docker build -t emccode/twittercord .


## Initial Contributors
Big thanks goes out to #DevHi5 and **emc {code&#7449;}**s
- Matt Cowger
- Jonas Rosland


## Future and Contributions
- Hyper-Media based REST API
- Better logging
- Control Plane API
- Other social media applications

Licensing
---------
Licensed under the Apache License, Version 2.0 (the “License”); you may not use this file except in compliance with the License. You may obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an “AS IS” BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

Support
-------
Please file bugs and issues at the Github issues page. For more general discussions you can contact the EMC Code team at <a href="https://groups.google.com/forum/#!forum/emccode-users">Google Groups</a>. The code and documentation are released with no warranties or SLAs and are intended to be supported through a community driven process.

 