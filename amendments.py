'''
Created on 13 Sep 2015

@author: alex
'''

import twitter
import credentials
import bitly_api
import datetime    
from funcs.ql import QuickList
from controllers import Robot, RobotMaster
import os
 
def tweet(status,media_url=None):
    print "tweeting"
    api = twitter.Api(**credentials.twitter_moonrover)
    if media_url:
        return api.PostMedia(status,media_url)
    else:
        return api.PostUpdate(status)
    
def make_link(url):

    c = bitly_api.Connection(access_token=credentials.bitly_access_token)
    return c.shorten(url)['url']

def do_process():
    
    local_loc = os.path.dirname(__file__)
    storage = QuickList().open(os.path.join(local_loc,"schedules//us-nara-amending-america-dataset-raw-2016-02-25.csv"))
    
    storage.shuffle()
    
    for r in storage:
        row = r
        break
        
    text  = "{0} - {1}".format(row["year"],row["title_or_description_from_source"])[:141] 
    
    print text

    
#rover = Robot("Moon Rover",do_process,minutes=1)

#RobotMaster().register(rover)

if __name__ == "__main__":
    do_process()
    #rover.tweet()