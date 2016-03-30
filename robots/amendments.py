'''
US Amendments - tweets proposed amedments to us constitution
the culture_chef built earlier
'''
if __name__ == "__main__":
    import sys
    sys.path.append("..")

from robot_core import Robot
from funcs.ql import QuickList
import os
 
class AmendmentBot(Robot):
    handle = "CultureReuseBot"
    twitter_credentials = {}
    minutes= 121
    
    def tweet(self):
        
        local_loc = os.path.dirname(__file__)
        storage = QuickList().open(os.path.join(local_loc,"schedules//us-nara-amending-america-dataset-raw-2016-02-25.csv"))
        
        storage.shuffle()
        
        for r in storage:
            row = r
            break
            
        text  = "{0} - {1}".format(row["year"],row["title_or_description_from_source"])[:141] 
        
        print text

    
if __name__ == "__main__":
    AmendmentBot().tweet()