"""
Title | Project

Authors: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 
Updated: 
License: MIT License <https://opensource.org/licenses/MIT>
"""


from datetime import datetime
myFile = open('append.txt', 'a') 
myFile.write('\nAccessed on ' + str(datetime.now()))
