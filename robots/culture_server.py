'''
Cultural Reuse Project - tweets the stored tweets off a schedule
the culture_chef built earlier
'''
if __name__ == "__main__":
    import sys
    sys.path.append("..")

import credentials
from robot_core import Robot
from robot_mixins import TumblrRobot
from funcs.ql import QuickList
import os
 
class CultureReuse(Robot, TumblrRobot):
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
            tweet = r["nice_title"]
            tags = [
                    r['title'],
                    str(r['year']),
                    "culture reuse"                   
                    ]
            tweets = self._tweet_video(tweet,file_loc)
            self._tumblr(tweet,video_url=str(file_loc),tags=tags)
            break
            
        return tweets
    
if __name__ == "__main__":
    CultureReuse().tweet_and_retweet()