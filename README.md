# traffic-monitor


TODO: 
1. Add documentation and installation instruction documentation. 
2. Add unit tests and end to end tests, and load test, and test where traffic TO server is intercepted (as opposed to just testing traffic out of server)
3. Add function documentation
4. Code cleanup
5. Modularize code

Functional todos:
3. UI output to fit prompt, and prettify
4. Make list of interesting stats to output
5. Alerting
6. Show other interesting stats
7. Explain how design could be improved

Ordering for tasks:
3. Interesting stats logic and UI cleanup (display sections not urls)
4. Testing for traffic TO server
5. Unit tests, integration tests, and e-e tests


Points to Improve:

Keep timeseries logs instead of just ip and dest url logs. 

Use numpy and cumsum to calculate rolling averages, instead of formula (for purposes of the project, stuck to from-scratch implementation to limit number of dependencies to make installation easier (also numpy/scipi are large and I didn't want to kill my vm or use cloud9). 

When calculating rolling averages, resetting the cumulative sum may be off by a couple seconds due to no explicit locking. However, http://effbot.org/zone/thread-synchronization.htm and https://stackoverflow.com/questions/2291069/is-python-variable-assignment-atomic 

There is a stats delay upon creation of new logfile. The 10 second stats aggregation reads only until the end of the current file. One has to wait until the next 10 second interval to read the newest file. 
