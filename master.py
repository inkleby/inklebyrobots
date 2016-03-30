'''
Master control script - run every minute and will check all robots in the 
robots directory to see if they should speak
'''

import credentials
from robot_core import Robot
from robots import * # triggers import of all robots in that directory

Robot.retweet_credentials = credentials.twitter_inklebyrobots
Robot.run_all()