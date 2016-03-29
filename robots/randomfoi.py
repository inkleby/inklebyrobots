# -*- coding: utf-8 -*-

'''
Created on 13 Sep 2015

randomfoi - tweets a random foi from whatdotheyknow.com


@author: alex
'''

if __name__ == "__main__":
    import sys
    sys.path.append("..")

import credentials
import random
import datetime

from robot_core import Robot
from robot_mixins import BitlyRobot, ImportIoRobot
    

    
class FOIRequest(BitlyRobot):
    """
    convert response from import io into useful object
    """
    
    def __init__(self,response):
        self.name = response['foi/_text']
        self.url = response['foi'].split("#")[0]
        self.status = response['status']
        
        """ split description up into different features"""
        junk = ["Follow up sent to ","Request sent to ","Response by "]
        seperators = [" on "," to "," by "]
        
        self.desc = response['desc']
        for j in junk:
            self.desc = self.desc.replace(j,"")
        for j in seperators:
            self.desc = self.desc.replace(j,",")
        splits = self.desc.split(",")
        if len(splits) <> 3:
            self.bad_format = True
            return None
        else:
            self.bad_format = False
        self.authority,self.requester,self.date = splits
        if self.date[1] == " ":
            self.date = "0" + self.date
        self.date = datetime.datetime.strptime(self.date,"%d %B %Y.")
        
    def get_short_link(self):
        return self.make_link(self.url)
    
    def format(self):
        return "{0} - {1} ({2}) {3}".format(self.name,
                                            self.authority,
                                            self.date.strftime("%b %y"),
                                            self.get_short_link())
      


class FOIRobot(Robot,ImportIoRobot):
    """
    robot finds a random FOI requests on they whatdotheyknow website
    and tweets it
    """
    handle = "randomfoi"
    twitter_credentials = credentials.twitter_randomfoi
    minutes=141
    uk_hours = True

    def get_page(self,page_no,start_date,end_date):
        """constructs search page to pass to import io"""
        
        def fd(date):
            dd = date.strftime("%d/%m/%Y")
            return dd.replace("/","%2F")
        
        connector =  "bb7ad470-5f69-4575-a3d5-999a990fd873"
        url_format = "https://www.whatdotheyknow.com/list/" \
                     "successful?page={0}&request_date_after={1}&request_date_before={2}"
        page = url_format.format(page_no,fd(start_date),fd(end_date))
        return self.import_io_api(connector,page)
    
        
    def random_date(self,start,end):
        """get random day for search"""
        import math
        days = (end-start).days 
        random.seed()
        #exponential weight towards end of range
        day = int(math.sqrt(random.randint(0,days**2))) 
        return start + datetime.timedelta(days=day)
    
    
    def get_random_page(self): 
        """site only offers 20 page in each search set - 
        need to move date ranges around to get historical searches"""
        start_range = datetime.datetime(year=2008,month=1,day=17)
        end_range = datetime.datetime.now()
        
        start_date = self.random_date(start_range,end_range)
        end_date = start_date + datetime.timedelta(days=40)
        
        random.seed()
        page = random.randint(1,5)
        return self.get_page(page,start_date,end_date)
        
        
    def get_text(self):
        text = ""
        fois = self.get_random_page()
        random.seed()
        if fois:
            formatted = [FOIRequest(x) for x in fois]
            #lazy, where default extractor not working - just give up
            formatted = [x for x in formatted if x.bad_format == False and x.status == "Successful."]  
            random.shuffle(formatted)
            for f in formatted:
                r = f.format()
                if len(r) < 135: #make sure result is actually tweetable
                    text = r
                    break
                
        return text

    def tweet(self):
    
        return [self._tweet(self.get_text())]
    
            

if __name__ == "__main__":
    FOIRobot().tweet()