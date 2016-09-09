#!/usr/bin/env python3
# Implement RESTFUL API to get table information from a database

from flask import Flask
from flask.ext.cors import CORS
import os
import config
from c_methods import login_manager


CORS(config.app)
login_manager.init_app(config.app)
#Set some secret key here
#Example: config.app.secret_key = os.urandom(50)
config.app.run(host="0.0.0.0", port=int("8080"), debug=True)
