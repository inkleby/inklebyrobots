'''
Created on 19 Sep 2015

@author: Alex
'''

from classes import RobotMaster
import oldillustration
import badhousingideas
import randomfoi
import credentials
r = RobotMaster()
r.register_retweet(credentials.twitter_inklebyrobots)
r.run()