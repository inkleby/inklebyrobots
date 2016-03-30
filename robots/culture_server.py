'''
Cultural Reuse Project - tweets the stored tweets off a schedule
the culture_chef built earlier
'''
if __name__ == "__main__":
    import sys
    sys.path.append("..")

import credentials
from robot_core import Robot
from robot_mixins import TumblrRobot, GfycatRobot
from funcs.ql import QuickList
import os
 
class CultureReuse(Robot, TumblrRobot, GfycatRobot):
    handle = "CultureReuseBot"
    twitter_credentials = credentials.twitter_culturalreuse
    retweet_credentials = credentials.twitter_inklebyrobots
    tumblr_blog = "culturereuse"
    minutes= 121

    def tweet(self):
        """
        extract a clip from the pool
        send to twitter and tumblr
        """
        library = os.path.join(os.path.dirname(__file__),
                               "..//libraries//reuse//")
                            
        ql = QuickList().open(os.path.join(library,"pool.xls"))
        
        ql.shuffle()
        
        for r in ql:
            file_loc = os.path.join(library,r["file_name"])
            text = r["nice_title"]
            tags = [
                    r['title'],
                    str(r['year']),
                    "culture reuse"                   
                    ]
            
            gif_url = self._upload_gif(file_loc)
            
            tumblr_text = '<p>{0}</p><p><a href="{1}">get from gfycat</a></p>'.format(text,gif_url)
            
            tumblr_link = self._tumblr(tumblr_text,video_url=str(file_loc),tags=tags)
            if tumblr_link:
                text += " {0}".format(tumblr_link)
            tweets = self._tweet_video(text,file_loc)
            
            break
            
        return tweets
    
if __name__ == "__main__":
    CultureReuse().tweet_and_retweet()