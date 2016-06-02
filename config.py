#!/usr/bin/env python
# Implement RESTFUL API to get table information from a database

from flask import Flask
from flask.ext.cors import CORS
from c_methods import dataModel,routeMaker

#Create a dictionary representing colums in dictionary
#'<col name>': None
fields = {
}

#create an object allowing access to fields and database 
#<database object> = dataModel("<table name>",fields,"<Config file with information for database.cfg","<Heading for config file")

app = Flask(__name__)
CORS(app)

#<route object> = routeMaker(<database object,"<desired route",app)

#Using to see what url's are being served
for rule in app.url_map.iter_rules():
	print(rule)


app.run(host="0.0.0.0", port=int("8080"), debug=True)

