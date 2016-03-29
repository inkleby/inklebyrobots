'''
Moon Rover - tweets the moon rover tweets off a schedule
'''

if __name__ == "__main__":
    import sys
    sys.path.append("..")

import credentials
from robot_schedule import ScheduleRobot
import os
 
class MoonRoverRobot(ScheduleRobot):
    handle = "WNTS_Rover"
    twitter_credentials = credentials.twitter_moonrover
    schedule = os.path.join(os.path.dirname(__file__),
                            "..//schedules//elevation_data.csv")
    
    
if __name__ == "__main__":
    MoonRoverRobot().tweet()