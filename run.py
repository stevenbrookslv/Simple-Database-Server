#!/usr/bin/env python3
# Implement RESTFUL API to get table information from a database

from flask import Flask
from flask.ext.cors import CORS
import config


CORS(config.app)
config.app.run(host="0.0.0.0", port=int("8080"), debug=True)
