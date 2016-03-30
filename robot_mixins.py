'''
Created on 28 Mar 2016

@author: Alex
'''

import bitly_api
from gfycat.client import GfycatClient
import pytumblr
import requests
import credentials
from imgurpython import ImgurClient
import time

class GfycatRobot(object):

    def _upload_gif(self,file_url):
        client = GfycatClient()
        print "uploading file to Gfycat"
        result = client.upload_from_file(file_url)
        name = result['gfyName']
        url = "https://gfycat.com/{0}".format(name)
        return url


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
        results = {}
        client = pytumblr.TumblrRestClient(**self.__class__.tumblr_creds)
        if self.__class__.tumblr_blog:
            if video_url:
                print "sending video to {0}".format(self.__class__.tumblr_blog)
                results = client.create_video(self.__class__.tumblr_blog,
                                            state="published",
                                            data=video_url,
                                            tags=tags,
                                            format="html",
                                            caption=text)                
                
            elif image_url:
                print "sending image to {0}".format(self.__class__.tumblr_blog)
                results = client.create_photo(self.__class__.tumblr_blog,
                                            state="published",
                                            tags=tags,
                                            format="markdown",
                                            source=image_url,
                                            caption=text)
            else:
                print "sending text to {0}".format(self.__class__.tumblr_blog)
                results = client.create_text(self.__class__.tumblr_blog,
                                           state="published",
                                           title="",
                                           tags=tags,
                                           body=text)
            
            
        if results:
            allowed_loops = 20
            latest = None
            while latest == None and allowed_loops > 0:
                post = client.posts(self.__class__.tumblr_blog,limit=1)
                post = post['posts'][0]
                if text not in post['trail'][0]['content_raw']:
                    print "no url yet, waiting for processing"
                    allowed_loops -= 1
                    time.sleep(10)
                else:
                    latest = True
                    
            short_url = post['short_url']
            return short_url
            
            
        else:
            url = None
        return url


if __name__ == "__main__":
    pass