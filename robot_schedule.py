'''
Created on 28 Mar 2016

@author: Alex
'''
'''
Created on 13 Sep 2015

@author: alex
'''

import datetime    
from funcs.ql import QuickList
from robot_core import Robot
from robot_mixins import BitlyRobot
import os
 

class Schedule(object):
    """
    holds a single possible tweet - with time info
    """
    
    def __init__(self,row):
        """
        process row of info
        """
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



class ScheduleRobot(Robot,BitlyRobot):
    """
    a generic robot that works from a schedule rather than an iterator
    """
    abstract = True
    schedule = ""
    minutes=1

    def tweet(self):
        tweets = []
        
        assert len(self.__class__.schedule) > 0
        
        storage = QuickList().open(self.__class__.schedule,use_unicode=True)
        
        schedules = []
        n = datetime.datetime.now()
        for r in storage:
            schedules.append(Schedule(r))
        
        for s in schedules:
            if s.time_to_tweet(n):
                tweets.extend(self.make_tweet(s))
                
        return tweets
    
    def make_tweet(self,schedule_obj):
        if schedule_obj.link:
            link = self.make_link(schedule_obj.link)
        else:
            link = None
        
        status = schedule_obj.tweet
        if link:
            status += " " + link
    
        result = self._tweet(status,schedule_obj.media)
    
        return [result]
    