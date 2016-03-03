'''
Created on 13 Sep 2015

@author: alex
'''

import twitter
import credentials
import bitly_api
import datetime    
from funcs.ql import QuickList
from classes import Robot, RobotMaster
import os
 
def tweet(status,file_url):
    print "tweeting"
    api = twitter.Api(**credentials.twitter_moonrover)
    if file_url:
        return api.PostMedia(status,file_url)
    else:
        return api.PostUpdate(status)
    
    
def make_link(url):

    c = bitly_api.Connection(access_token=credentials.bitly_access_token)
    return c.shorten(url)['url']

class Schedule(object):
    
    def __init__(self,row):
        self.tweet = row["tweet"]
        try:
            self.time = datetime.datetime.strptime(row["time"],"%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            self.time = datetime.datetime.strptime(row["time"],"%Y-%m-%d %H:%M:%S")
        self.link = row["link"]
        self.media = row["media"]
    
    def time_to_tweet(self,n):
        """ is this tweet ready to be sent """
        bn = n - datetime.timedelta(minutes=1)
        return self.time >= bn and self.time < n

    def do_tweet(self):
        if self.link:
            link =  make_link(self.link)
        else:
            link = None
        
        status = self.tweet
        if link:
            status += " " + link
    
        result = tweet(status,self.media)
    
        return [result]
        
def do_process():
    tweets = []
    
    local_loc = os.path.dirname(__file__)
    storage = QuickList().open(os.path.join(local_loc,"schedules//elevation_data.csv"),unicode=True)
    
    schedules = []
    n = datetime.datetime.now()
    for r in storage:
        schedules.append(Schedule(r))
    
    for s in schedules:
        if s.time_to_tweet(n):
            tweets.extend(s.do_tweet())
            
    return tweets

    
rover = Robot("Moon Rover",do_process,minutes=1)

RobotMaster().register(rover)

if __name__ == "__main__":
    rover.tweet()