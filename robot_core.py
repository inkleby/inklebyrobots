'''
robot_core

Contains the main robot function. 

All robots are subclasses of this one.

@author: @alexparsons
'''
import os
import math
import sys
import time
import datetime
import twitter
from TwitterAPI import TwitterAPI
import six

class MetaRobot(type):
    registered = []

    def __new__(cls, name, parents, dct):

        abstract = False
        if "abstract" in dct:
            abstract = dct["abstract"]
        else:
            dct["abstract"] = False

        ncls = super(MetaRobot, cls).__new__(cls, name, parents, dct)
        
        if abstract == False and hasattr(ncls,"_all_robots"):
            ncls._all_robots.append(ncls)
            
        return ncls


class BaseRobot(object,six.with_metaclass(MetaRobot)):
    """
    handles basic communication with twitter
    """
    twitter_credentials = {}
    retweet_credentials = {}
    abstract = True
    
    @classmethod
    def clear_credentials(cls):
        api = twitter.Api(**cls.twitter_credentials)
        tweets = api.GetUserTimeline(screen_name = cls.handle)
        for t in tweets[:100]:
            print api.DestroyStatus(t.id)
     
    def _tweet(self,status,media_file_url=None):
        print "tweeting"
        try:
            api = twitter.Api(**self.__class__.twitter_credentials)
            if media_file_url:
                return api.PostMedia(status,media_file_url)
            else:
                return api.PostUpdate(status)
        except twitter.error.TwitterError,e:
            print e
            
    def _tweet_video(self,status,media_location=None):
        """
        chunked method to upload video
        #https://github.com/geduldig/TwitterAPI/blob/master/examples/upload_video.py
        """
        
        api = TwitterAPI(**self.__class__.twitter_credentials)
        
        
        bytes_sent = 0
        total_bytes = os.path.getsize(media_location)
        file = open(media_location, 'rb')
        
        def check_status(r):
            if r.status_code < 200 or r.status_code > 299:
                print(r.status_code)
                print(r.text)
                sys.exit(0)

        
        r = api.request('media/upload', {'command':'INIT',
                                         'media_type':'video/mp4',
                                         'total_bytes':total_bytes})
        check_status(r)
        
        media_id = r.json()['media_id']
        segment_id = 0
        
        while bytes_sent < total_bytes:
            chunk = file.read(4*1024*1024)
            r = api.request('media/upload', {'command':'APPEND',
                                             'media_id':media_id,
                                             'segment_index':segment_id},
                                             {'media':chunk})
            check_status(r)
            segment_id = segment_id + 1
            bytes_sent = file.tell()
            print('[' + str(total_bytes) + ']', str(bytes_sent))

        r = api.request('media/upload', {'command':'FINALIZE',
                                         'media_id':media_id})
        check_status(r)
        
        r = api.request('statuses/update', {'status':status,
                                            'media_ids':media_id})
        check_status(r)
        return [r.json()['id']]
        
    @classmethod
    def tweet_and_retweet(cls):
        """
        tweet and retweet if possible
        """
        tweets = cls().tweet()
        if isinstance(tweets,twitter.status.Status):
            tweets = [tweets]
        cls.retweet(tweets)
        
    @classmethod
    def retweet(cls,tweets):
        if cls.retweet_credentials and tweets:
            api = twitter.Api(**cls.retweet_credentials)
            for t in tweets:
                if isinstance(t,long): # allows for other api return ids rather than expected object
                    api.PostRetweet(t)
                else:
                    api.PostRetweet(t.id)

class Robot(BaseRobot):
    """
    Robot class that holds the generic tweeting functions
    All robots should be a subclass of this.
    
    minutes or hours tells it long to wait between each tweet
    uk_hours restricts to uk working hours
    force_run is a boolean that means it will always tweet.
    
    override tweet function to create new robot - needs to call _tweet
    
    """
    _all_robots = []
    minutes = 0
    hours = 0
    uk_hours = False
    force_run = False
    handle = ""
    abstract = True
        
    @classmethod
    def run_all(cls,**kwargs):   
        """
        run all robots - effectively talk to all
        registered subclasses.
        """

        seconds = time.time()
        minutes = math.floor(seconds/60)
        hours = minutes/60
    
        robot_count = 0
        for b in cls._all_robots:
            b.check_and_run(minutes=minutes,hours=hours)
            robot_count += 1
        print "{0} robots run".format(robot_count)
        
    @classmethod
    def check_and_run(cls,**kwargs):
        """
        do we pass the check function? If so, tweet and retweet
        """
        print "Checking for tweets for {0}".format(cls.handle)
        if cls().check(**kwargs):
            cls.tweet_and_retweet()

    def populate(self,number_to_generate=50):
        """
        add 50 entries in quick succession
        """
        for x in range(0,number_to_generate):
            self.tweet()
            time.sleep(2)
        
        
    def check(self,minutes,hours):
        """
        Sees if correct number of minutes or hours have passed 
        since the epoch
        to run the tweet function
        
        Override if this isn't a timing based bot.
        
        Returns boolean 
        
        """
        
        timings = {"hours":hours,
                   "minutes":minutes}
        
        if self.__class__.force_run:
            print "forcing"
            return True
        
        if self.__class__.uk_hours:
            hour = datetime.datetime.now().hour
            if hour <6 or hour > 22:
                return False
        
        lengths = ['minutes','hours']
        for l in lengths:
            if getattr(self.__class__,l):
                if timings[l] % getattr(self,l) == 0: 
                    return True
        
        return False
    
    def tweet(self):
        """
        should be overridden with the function that governs contents
        pass tweets to _tweet - return list of tweets or individual tweet
        return
        """
        return []
    
    