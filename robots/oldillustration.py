'''
Basic flickr bot that reads a random page from the british library's collection and tweets it
'''
import flickrapi
import random 
import credentials
    
from robot_core import Robot
from robot_mixins import BitlyRobot


class FlickrRobot(Robot,BitlyRobot):
    """
    tweet a random picture from a flickr account
    """
    url_template = 'http://farm%(farm_id)s.staticflickr.com/%(server_id)s/%(photo_id)s_%(secret)s.jpg'
    web_url = "https://www.flickr.com/photos/britishlibrary/{0}"
    user_id = "12403504@N02"
    no_of_pages = 10000
    handle = "oldillustration"
    minutes = 79
    twitter_credentials = credentials.twitter_oldillustrations
    
    @classmethod
    def get_random_photo(cls):
    
        def url_for_photo(p,year):
            photo_url= cls.url_template % {
                'server_id': p.get('server'),
                'farm_id': p.get('farm'),
                'photo_id': p.get('id'),
                'secret': p.get('secret'),
            }
            page_url = cls.web_url.format(p.get('id'))
            return photo_url, page_url,p.get("title"),year
        
        flickr = flickrapi.FlickrAPI(credentials.flickr_api_key, credentials.flickr_api_secret)
        
        random.seed()
        page_no = random.randint(1,cls.no_of_pages)
        
        result = random.choice(flickr.photos_search(user_id=cls.user_id,
                                                    per_page=20,
                                                    page=page_no)[0]) 
        
        photo_info = flickr.photos_getInfo(photo_id=result.get('id'),
                                     secret=result.get('secret')).find("photo")
                                     
        desc = photo_info.find("description").text
        
        year = None
        for r in desc.split("\n"):
            if "Date of Publishing" in r:
                year = r.split(":")[1].strip()
                break
            
        return url_for_photo(result,year)
 
    def tweet(self):
        photo_url, web_url, title,year = self.__class__.get_random_photo()
        
        short =  self.make_link(web_url)
        
        status = title.replace("Image taken from page ","From p. ")
    
        status = status[:60] + "... " + "({0}) ".format(year) + short
    
        result = self._tweet(status,photo_url)
    
        return [result]
 
    

if __name__ == "__main__":
    FlickrRobot().tweet()