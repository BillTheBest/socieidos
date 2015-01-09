from flask import Flask, render_template
from pprint import pprint, pformat
import logging
import requests
from threading import Thread
import boto
from boto.s3.connection import OrdinaryCallingFormat
from boto.s3.key import Key
from boto.s3.lifecycle import Lifecycle, Expiration
import uuid
from TwitterAPI import TwitterAPI,TwitterRestPager
from datetime import timedelta
from default_config import *
import random
import time
import os
from apscheduler.schedulers.background import BackgroundScheduler
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import json

scheduler = BackgroundScheduler()

cache_opts = {
    'cache.type': 'memory',
}
cache = CacheManager(**parse_cache_config_options(cache_opts))

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(filename)s: '
                                '%(levelname)s: '
                                '%(funcName)s(): '
                                '%(lineno)d:\t'
                                '%(message)s')

app = Flask(__name__)
img_session = requests.Session()

s3conn = eval(lc_s3_connect)

while True:
    try:
        bucket = s3conn.get_bucket(lc_s3_bucket_name)
        break
    except Exception,e:
        logging.error(str(e))

    try:
        logging.info('Creating bucket: '+lc_s3_bucket_name)
        s3conn.create_bucket(lc_s3_bucket_name)
    except Exception,e:
        logging.error(str(e))

    time.sleep(1)



def check_coords(grid,point):
   return grid[0] < point[1] < grid[2] and grid[1] < point[0] < grid[3]

def watch_tweet_stream(s3_store,
                       s3_store_in,
                       s3_object_expiration_time,
                       twitter_keys=[],
                       twitter_request='statuses/filter',
                       twitter_filter={'track':''},
                       check_geo_coords=False,
                       geo_box_coords_long_lat='',
                       check_retweeted_status=False,
                       check_possibly_sensitive=False):
    api = TwitterAPI(twitter_keys[0],twitter_keys[1],twitter_keys[2],twitter_keys[3])

    while True:
        try:
            response = api.request(twitter_request,twitter_filter)
            for item in response.get_iterator():
                if 'text' in item:
                    if check_retweeted_status and 'retweeted_status' in item and item['retweeted_status']:
                        logging.info("Tweet is a retweet.")
                        continue
                    if check_possibly_sensitive and 'possibly_sensitive' in item and item['possibly_sensitive']:
                        logging.info("Tweet is possibly sensitive.")
                        continue
                    if check_possibly_sensitive and 'retweet' in item and 'possibly_sensitive' in item['retweet'] and item['retweet']['possibly_sensitive']:
                        logging.info("Tweet is a retweet and possibly sensitive.")
                        continue            
                    if check_geo_coords and item['geo'] is None:
                        logging.info("Geo tag not set.")
                        continue
                    if check_geo_coords and not check_coords(get_coord_array(geo_box_coords_long_lat),item['geo']['coordinates']):
                        logging.info("Tweet not in region.")
                        continue
                    if 'entities' in item and 'media' in item['entities']:
                        logging.info('Tweet: '+'@'+item['user']['screen_name']+':'+item['text'])
                        for media_object in item['entities']['media']:
                            if media_object['type'] == 'photo':
                                    if s3_store:
                                        logging.info("Dispatching thread to capture for: " + media_object['media_url'] + " with filter: " + str(twitter_filter) + " and storing in " + s3_store_in.lower())
                                        t = Thread(target=capture_photo_to_object,args=(s3_object_expiration_time,media_object['media_url'],s3_store_in.lower(),))
                                        t.start()
                                    else:
                                        logging.info('Not storing tweet since s3_store is False.')
                            else:
                                logging.info('Tweet media is not a photo.')
                    else:
                        logging.info('Tweet does not have media.')
                elif 'message' in item and item['code'] == 88:
                    print 'SUSPEND, RATE LIMIT EXCEEDED: %s\n' % item['message']
                break
        except Exception,e:
            logging.error(str(e))
            logging.debug("Sleeping for 30 seconds")
            time.sleep(30)



def get_coord_array(geo_box_coords_long_lat):
    return [float(n) for n in geo_box_coords_long_lat.split(',')]

def delete_old_keys(store_in,object_max_age):
    list_of_keys = list(bucket.list(store_in))
    current_time = time.time()
    to_delete = []
    for key in list_of_keys:
        hashtag,timestamp,guid = key.name.split('/')
        timestamp = int(timestamp)
        if len(list_of_keys) > lc_min_items and current_time > timestamp + object_max_age:
            to_delete.append(key)
            list_of_keys.remove(key)

    results = bucket.delete_keys(to_delete)
    logging.info("Deleted")
    logging.info("Errors")
    logging.info(results.errors)



def capture_photo_to_object(s3_object_expiration_time,
                            url=None, 
                            hashtag=None):
    """

    :param url: string
    :return: :rtype: string
    """
    if url is None: return False

    expiry_time = eval(s3_object_expiration_time)
    image_response = img_session.get(url)
    if image_response.status_code == 200:
        logging.debug("Grabbed image from %s" % url)
        guid = str(uuid.uuid4())
        k = Key(bucket)
        timestamp = str(int(time.time()))
        k.key = "/".join([hashtag,timestamp,guid])
        logging.debug("Uploading %s as %s" % (k.key,image_response.headers.get('content-type')))
        k.set_contents_from_string(image_response.content)
        return k.key
    else:
        logging.warning("Failed to grab %s" % url)
        return None

@cache.cache('get_keys_for_hashtag', expire=lc_get_objects_query_cache_seconds)
def get_keys_for_hashtag(hashtag,return_limit=25,):
    candidates = list(bucket.list(hashtag))
    max_return = min(len(candidates),return_limit)
    return (candidates[:-max_return])[::-1]

def get_object_url_from_key(key,s3_object_url_timeout):
    return key.generate_url(s3_object_url_timeout)



watch = Thread(target=watch_tweet_stream, args=(eval(lc_s3_store),
                                                lc_s3_store_in,
                                                lc_s3_object_expiration_time,
                                                eval(lc_twitter_keys),
                                                lc_twitter_request,
                                                eval(lc_twitter_filter),
                                                eval(lc_check_geo_coords),
                                                lc_geo_box_coords_long_lat,
                                                eval(lc_check_retweeted_status),
                                                eval(lc_check_possibly_sensitive),
                                                ))
watch.daemon = True
watch.start()

def create_hash_objects(dict):
    return {
        'response': {
            'requested_objects':[dict['s3_store_in']],
            'objects':[{ 'object_url':url} for url in dict['urls'] ],
            'type':"image",
            'source':"twitter",
            'metdata':{}
        }
    }

def create_array_urls(s3_object_url_timeout,s3_store_in):
    urls = [get_object_url_from_key(key,s3_object_url_timeout) for key in get_keys_for_hashtag(s3_store_in)]
    dict = {'s3_store_in':lc_s3_store_in,'urls':urls}
    return dict

@app.route('/')
def dashboard():
    dict = create_array_urls(lc_s3_object_url_timeout,lc_s3_store_in)
    objects = create_hash_objects(dict)
    return render_template('default.html',objects=objects['response']['objects'])

@app.route('/v1/objects', methods=['GET'])
def get_objects():
    dict = create_array_urls(lc_s3_object_url_timeout,lc_s3_store_in)
    objects = create_hash_objects(dict)
    return json.dumps(objects,sort_keys = False, indent = 4) 

if __name__ == '__main__':
    scheduler.add_job(delete_old_keys,'interval',args=(lc_s3_store_in,lc_s3_object_max_age,),minutes=lc_job_s3_interval_delete_old_objects_minutes)
    scheduler.start()
    port = 8080
    app.run(debug=False,port=int(port),host='0.0.0.0',threaded=True)

