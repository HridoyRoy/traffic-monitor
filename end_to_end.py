import subprocess
import os
import time
import json
import shutil

# Let's start the monitor
monitor_proc = subprocess.Popen(["python3", "-m", "t_monitor"])

# Great! Now, let's add some requests

for i in range(5):
    time.sleep(2)
    os.system("curl www.google.com")
    
# Okay. We will first verify no alerts have been generated, as our request ratio is .5 requests per second
assert os.path.exists("./saved") is True
assert os.path.exists("./saved/alerts.txt") is False
    
# Let's test the logger's basic functionality by making sure 5 logs have been generated. 
assert os.path.exists("./saved/log0.txt") is True
count = 0
with open("./saved/log0.txt") as log:
    for line in log:
        count += 1

 # 5 logs in log0.txt means the count is now at 5
assert count == 5

# Okay! Let's continue testing the logger! Note that our log file size is 10 (defined in globals.py). Let's generate 11 logs (6 for facebook), and make sure 2 files are generated. 

for i in range(6):
    time.sleep(2)
    os.system("curl www.facebook.com")

# Still no alerts
assert os.path.exists("./saved/alerts.txt") is False
assert os.path.exists("./saved/log1.txt") is True

# check that log0 has 10 lines, and log1 has 1 line. 
count = 0
with open("./saved/log0.txt") as log:
    for line in log:
        count += 1

assert count == 10

count = 0
with open("./saved/log1.txt") as log:
    for line in log:
        count += 1

assert count == 1

# Excellent. So our Logger has basic functionality covered. Now let's test the statistician. Let's wait for the statistician to run again (wait 10 seconds) and then verify that facebook has the most hits.

time.sleep(10)

with open("./saved/stats.txt") as stats_file:
    stat_data = json.load(stats_file)
    assert stat_data[0].get("most_hits_section") == "www.facebook.com/"

# Okay! Now we will test the Averager and alerting mechanism. Let's set off an alert, and verify that an alert is logged. We will wait and verify that the resolution of the alert is also logged. We will set off a second alert and verify that a second alert log is added, and wait for the resolution of that as well. 

# Recall that our current alert threshold is .5

# This test has gone on for approximately 45 seconds, and we have 11 requests so far. So the average number of requests seen is approximately 10/45 = approximately .22. Let's shoot this value up to 30 / 50 > .5, and make sure we get an alert

for i in range(20):
    os.system("curl www.google.com/scholar")

# Let's wait a small delta for the averager to do its thing (averager polls every second)
time.sleep(3)

# The alerts file should have been created, and should be populated with a message that starts with "High traffic generated an alert". Let's see if that is the case. 

assert os.path.exists("./saved/alerts.txt") is True
count = 0
with open("./saved/alerts.txt", "r") as alerts:
    for line in alerts:
        count += 1
    assert count == 1
    assert line.startswith("High traffic generated an alert") is True

# Okay, great! Now, let's wait 15 seconds + some delta so we are at 30 / 65 < .5, and verify that the alert resolution log has been added. This log begins with the word "Recovered".  

time.sleep(20)
count = 0
with open("./saved/alerts.txt", "r") as alerts:
    for line in alerts:
        count += 1
    assert count == 2
    assert line.startswith("Recovered")

# Looks promising. Now, let's add 20 + some delta number of requests so we are at 50 / 70 > .5, and verify that another alert is fired, so our alert history is at 2 alerts and 1 resolution. 

for i in range(30):
    os.system("curl www.google.com")
count = 0
with open("./saved/alerts.txt", "r") as alerts:
    for line in alerts:
        count += 1
    assert count == 3
    assert line.startswith("High traffic generated an alert") is True

# Let's wait 40 + delta number of seconds and verify that our alert has resolved (50 / 110 < .5). Note that the math has become quite convoluted, due to certain curl requests taking longer than other curl requests (google curl requests to the homepage are slow). But the idea holds.  

time.sleep(65)
count = 0
with open("./saved/alerts.txt", "r") as alerts:
    for line in alerts:
        count += 1
    assert count == 4
    assert line.startswith("Recovered")

# We are done! We have end to end the traffic monitor's basic functionality, isolating each class that has been tested in each section! Let's kill the traffic monitor and clean up the saved directory! 
subprocess.Popen.kill(monitor_proc)
shutil.rmtree("./saved")
