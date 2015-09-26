# -*- coding: utf-8 -*-

'''
Created on 13 Sep 2015

randomfoi - tweets a random foi from whatdotheyknow.com


@author: alex
'''
import twitter
import credentials
import bitly_api
import requests
import random
import datetime

from classes import Robot, RobotMaster

    
def make_link(url):

    c = bitly_api.Connection(access_token=credentials.bitly_access_token)
    return c.shorten(url)['url']
    
    
def import_io_api(key,user,connector,url):
    """ generic code for connecting to import io code"""
    
    api_url = "https://api.import.io/store/data/{0}/_query".format(connector)
    
    data = {'input/webpage/url':url,'_user':user ,'_apikey':key}
    r = requests.get(api_url, params=data)
    #print r.url
    try:
        result =  r.json()
    except ValueError:
        return None
        
    
    try:
        return result['results']
    except KeyError:
        return None
    

def get_page(page_no,start_date,end_date):
    """constructs search page to pass to import io"""
    def fd(date):
        dd = date.strftime("%d/%m/%Y")
        return dd.replace("/","%2F")

    key = credentials.import_io_key
    user = credentials.import_io_user
    connector =  "bb7ad470-5f69-4575-a3d5-999a990fd873"
    page = "https://www.whatdotheyknow.com/list/successful?page={0}&request_date_after={1}&request_date_before={2}".format(page_no,fd(start_date),fd(end_date))
    return import_io_api(key, user,connector,page)

    
def random_date(start,end):
    import math
    """get random day for search"""
    days = (end-start).days 
    random.seed()
    day = int(math.sqrt(random.randint(0,days**2))) #exponential weight towards end of range
    return start + datetime.timedelta(days=day)
    
    
    
def get_random_page(): 
    """site only offers 20 page in each search set - need to move date ranges around to get historical searches"""
    start_range = datetime.datetime(year=2008,month=1,day=17)
    end_range = datetime.datetime.now()
    
    start_date = random_date(start_range,end_range)
    end_date = start_date + datetime.timedelta(days=40)
    
    random.seed()
    page = random.randint(1,5)
    return get_page(page,start_date,end_date)
    
class FOIRequest(object):
    
    def __init__(self,response):
        self.name = response['foi/_text']
        self.url = response['foi']
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
        return make_link(self.url)
    
    def format(self):
        return "{0} - {1} ({2}) {3}".format(self.name,self.authority,self.date.strftime("%b %y"),self.get_short_link())
        
        
def get_text():
    text = ""
    fois = get_random_page()
    random.seed()
    if fois:
        formatted = [FOIRequest(x) for x in fois]
        formatted = [x for x in formatted if x.bad_format == False and x.status == "Successful."]  #lazy, where default extractor not working - just give up
        random.shuffle(formatted)
        for f in formatted:
            r = f.format()
            if len(r) < 135: #make sure result is actually tweetable
                text = r
                break
            
    return text




def tweet():

    api = twitter.Api(**credentials.twitter_randomfoi)
    try:
        tx = get_text()
        if tx:
            return api.PostUpdate(tx)
    except twitter.error.TwitterError,e:
        print e
        
randomfoi = Robot("Randomfoi",tweet,minutes=141,uk_hours=True)

RobotMaster().register(randomfoi)

if __name__ == "__main__":
    randomfoi.tweet()