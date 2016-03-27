'''
Created on 13 Sep 2015

@author: alex
'''
import flickrapi
import random 
import twitter
import credentials
import bitly_api
    
from controllers import Robot, RobotMaster

url_template = 'http://farm%(farm_id)s.staticflickr.com/%(server_id)s/%(photo_id)s_%(secret)s.jpg'
web_url = "https://www.flickr.com/photos/britishlibrary/{0}"
no_of_pages = 10000


def get_random_photo():

    def url_for_photo(p,year):
        photo_url= url_template % {
            'server_id': p.get('server'),
            'farm_id': p.get('farm'),
            'photo_id': p.get('id'),
            'secret': p.get('secret'),
        }
        page_url = web_url.format(p.get('id'))
        return photo_url, page_url,p.get("title"),year
    
    flickr = flickrapi.FlickrAPI(credentials.flickr_api_key, credentials.flickr_api_secret)
    
    random.seed()
    page_no = random.randint(1,no_of_pages)
    
    result = random.choice(flickr.photos_search(user_id="12403504@N02", per_page=20,page=page_no)[0]) 
    
    desc = flickr.photos_getInfo(photo_id=result.get('id'),secret=result.get('secret')).find("photo").find("description").text
    
    year = None
    for r in desc.split("\n"):
        if "Date of Publishing" in r:
            year = r.split(":")[1].strip()
            break
        
    return url_for_photo(result,year)
 
 
def tweet(status,file_url):

    api = twitter.Api(**credentials.twitter_oldillustrations)   
    return api.PostMedia(status,file_url)
    
    
def make_link(url):

    c = bitly_api.Connection(access_token=credentials.bitly_access_token)
    return c.shorten(url)['url']
    
    
def do_process():
    photo_url, web_url, title,year = get_random_photo()
    
    short =  make_link(web_url)
    
    status = title.replace("Image taken from page ","From p. ")

    
    status = status[:60] + "... " + "({0}) ".format(year) + short

    result = tweet(status,photo_url)

    return [result]
    
    
illustrations = Robot("Old Illustrations",do_process,minutes=79)

RobotMaster().register(illustrations)

if __name__ == "__main__":
    illustrations.tweet()