'''
Created on 28 Mar 2016

@author: Alex
'''

import bitly_api

import pytumblr
import requests
import credentials
from imgurpython import ImgurClient

class ImgurRobot(object):
    imgur_creds = credentials.imgur_credentials

    def get_image(self,image_id):
        client = ImgurClient(**self.__class__.imgur_creds)
        image = client.get_image(image_id)
        return image
    

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
        
class TumblrRobot(object):
    tumblr_creds = credentials.tumblr_credentials
    tumblr_blog = ""
    
    def _tumblr(self,text,image_url=None,video_url=None,tags=[]):
        """
        send image to tumblr
        """
        client = pytumblr.TumblrRestClient(**self.__class__.tumblr_creds)
        if self.__class__.tumblr_blog:
            if video_url:
                print "sending video to {0}".format(self.__class__.tumblr_blog)
                client.create_video(self.__class__.tumblr_blog,
                                    state="published",
                                    data=video_url,
                                    tags=tags,
                                    format="html",
                                    caption=text)                
                
            elif image_url:
                print "sending image to {0}".format(self.__class__.tumblr_blog)
                client.create_photo(self.__class__.tumblr_blog,
                                    state="published",
                                    tags=tags,
                                    format="markdown",
                                    source=image_url,
                                    caption=text)
            else:
                print "sending text to {0}".format(self.__class__.tumblr_blog)
                client.create_text(self.__class__.tumblr_blog,
                                   state="published",
                                   title="",
                                   tags=tags,
                                   body=text)


if __name__ == "__main__":
    pass