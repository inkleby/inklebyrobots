'''
US Amendments - tweets proposed ammendments to us constitution

from: http://www.archives.gov/open/dataset-amendments.html

'''

if __name__ == "__main__":
    import sys
    sys.path.append("..")
    
import credentials
from robot_core import Robot
from funcs.ql import QuickList
from robot_mixins import PastebinRobot
import os
import time
 

 
 
class AmendmentBot(Robot, PastebinRobot):
    handle = "USAmendments"
    twitter_credentials = credentials.twitter_almostamends
    minutes= 135
    
    def get_amendment_link(self,row):
        """constructs url page"""
        
        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4]) #adds ordinal stuff
        
        url = "https://www.congress.gov/bill/{0}-congress/{2}-joint-resolution/{1}"
        
        if row["joint_resolution_chamber"] == "House Joint Resolution":
            house = "house"
        else:
            house = "senate"
        
        url = url.format(ordinal(int(row["congress"])),int(row['joint_resolution_number']),house)
        
        return url
    
    
    def tweet(self):
        
        local_loc = os.path.dirname(__file__)
        storage = QuickList().open(os.path.join(local_loc,
                                                "..//schedules//us-nara-amending-america-dataset-raw-2016-02-25.xls"))
        
        storage.shuffle()
        storage.data = storage.data[:1]
        for r in storage:
            
            if r["year"] and r["title_or_description_from_source"]:
                row = r
                
                desc = row["title_or_description_from_source"]
                """
                remove generic phrasing
                """
                bad_terms=[
                           "Proposing an amendment to the Constitution of the United States relating to ",
                           "Proposing an amendment to the Constitution of the United States",
                           "A joint resolution proposing an amendment to the Constitution of the United States",
                           " to the Constitution of the United States.",
                           "A joint resolution proposing",
                           "A joint resolution proposing an amendment to the Constitution of the United States relative to ",
                           ]
                
                bad_terms.sort(key=lambda x:len(x), reverse=True)
                    
                for b in bad_terms:
                    desc = desc.replace(b,"")
                    
                    
                """
                fix formatting
                """
                desc = desc.strip()    
                if desc[0] == desc[0].lower():
                    desc = desc[0].upper() + desc[1:]
                    
                    
                """
                are we able to provide a link to this?
                """
                
                if row["year"] >= 1973 and row['joint_resolution_number']:
                    link = self.get_amendment_link(row)
                    allowed_length = 141 - 22
                elif row['source_code'] == "A":
                    #link = "book"
                    #allowed_length = 141 -22
                    link = None
                else:
                    link = None
                    allowed_length  = 141
                                    
                text  = u"{0} - {1}".format(int(row["year"]),desc)
                
                if len(text) > allowed_length:
                    long_text = text
                    if link == None:
                        #get pastebin version of this and get ready to link it
                        #link = self._paste_to_pastebin(long_text)
                        if link: #pastebin might fail
                            allowed_length = 141 -22
                    text = text[:allowed_length-3] + "..."
                    
                if link:
                    text += " " + link
                
                self._tweet(text)

    
if __name__ == "__main__":
    AmendmentBot().tweet()