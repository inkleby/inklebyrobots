'''
Created on 19 Sep 2015

@author: @alexparsons
'''

import math
import time
import datetime
import twitter



class RobotMaster(object):
    """
    robot master checks all registered bots to see if they should tweet
    """
    bots = []
    
    def __init__(self):
        
        self.bots = RobotMaster.bots
        
        self.seconds = time.time()
        self.minutes = math.floor(self.seconds/60)
        self.hours = self.minutes/60
        self.retweet_creds = None
        
    def register(self,bot):
        self.bots.append(bot)
        
    def register_retweet(self,cres): # pass a dictionary of credentials to have one account retweet all bots
        self.retweet_creds = cres
        
        
    def retweet(self,tweets):
        
        if self.retweet_creds and tweets:
            api = twitter.Api(**self.retweet_creds)
            for t in tweets:
                api.PostRetweet(t.id)
        
        
    def run(self):
        
        robot_count = 0
        tweets = []
        print "checking for pending robots"
        for b in self.bots:
            if b.check(self):
                robot_count += 1
                result = b.tweet()
                if result:
                    if isinstance(result,list):
                        tweets.extend(result)
                    if isinstance(result,twitter.status.Status):
                        tweets.append(result)

        self.retweet(tweets)
        print "{0} robots run".format(robot_count)
        


class Robot(object):
    """
    Robot class that holds the tweet functions
    """
    def __init__(self,name,tweet_function=None,*args,**kwargs):
        
        self.name = name
        self.minutes = 0
        self.hours = 0 
        self.uk_hours = False
        self.force_run = False
        self._tweet = tweet_function
        self.__dict__.update(**kwargs)
        
    def check(self,master):
        """
        Sees if correct number of minutes or hours have passed since the epoch
        """
        
        if self.force_run:
            print "forcing"
            return True
        
        if self.uk_hours:
            hour = datetime.datetime.now().hour
            if hour <6 or hour > 22:
                return False
        
        lengths = ['minutes','hours']
        for l in lengths:
            if getattr(self,l):
                if getattr(master,l) % getattr(self,l) == 0:
                    return True
        
        return False
        
    def clear_credentials(self,creds,name):
        api = twitter.Api(**creds)
        tweets = api.GetUserTimeline(screen_name = name)
        for t in tweets[:100]:
            print api.DestroyStatus(t.id)
        
                    
    def tweet(self):
        print "tweeting {0}".format(self.name)
        return self._tweet()
        print "done"
        
    def populate(self,number_to_generate=50):
        #adds 50 entries in quick succession
        for x in range(0,number_to_generate):
            self.tweet()
            time.sleep(2)
    

