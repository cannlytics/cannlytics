"""
Title | Project

Authors: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 
Updated: 
License: MIT License <https://opensource.org/licenses/MIT>
"""

from crontab import CronTab
 
my_cron = CronTab(tab="""*/1 * * * * python test_cron.py""")
# job = my_cron.new(command='python test_cron.py')
# job.minute.every(1)
 
my_cron.write()