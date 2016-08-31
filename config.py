#!/usr/bin/env python3
# Implement RESTFUL API to get table information from a database

from flask import Flask
from c_methods import dataModel,routeMaker
from manage import userManage
app = Flask(__name__)


#Create a dictionary representing colums in dictionary
#'<col name>': None
fields = {
}

#create an object allowing access to fields and database 
#<database object> = dataModel("<table name>",fields,"<Config file with information for database.cfg","<Heading for config file")

#<route object> = routeMaker(<database object,"<desired route",app,secureWrites=<true/false>)

#<user management object> = userMangage(<route object>)

#Using to see what url's are being served
for rule in app.url_map.iter_rules():
	print(rule)
