
# Server monitoring script

This python script monitors the server task in a regular interval. Script make a REST API, developed by flask, 
call for checking a databas table and return data in json format. Based on the returned data other tasks will be
executed. For example communicating with few more tables to store and retrive data, send status of script/command line/http_request 
to the specified location. Also maintain the history.  


## Technologies

Python 3.6, flask, Mysql


## Authors

* **ABU YUSUF** - [mayusuf](https://github.com/mayusuf)
