'''
Created on 28 Mar 2016

@author: Alex
'''

import bitly_api
import requests
import credentials


class BitlyRobot(object):
    """
    functions to talk to other apis and get details
    """
    bitly_access_token = credentials.bitly_access_token
    
    def make_link(self,url):
    
        c = bitly_api.Connection(access_token=self.__class__.bitly_access_token)
        return c.shorten(url)['url']
    
    
class ImportIoRobot(object):
    
    key = credentials.import_io_key
    user = credentials.import_io_user
    
    
    def import_io_api(self,connector,url):
        """ generic code for connecting to import io code"""
        
        api_url_format = "https://api.import.io/store/data/{0}/_query"
        
        api_url = api_url_format.format(connector)
        
        data = {'input/webpage/url':url,
                '_user':self.__class__.user,
                '_apikey':self.__class__.key}
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