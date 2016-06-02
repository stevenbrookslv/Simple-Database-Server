#!/usr/bin/python3
from flask import request, Response, Blueprint
import configparser
import uuid
import re,os,sys
import simplejson
import mysql.connector #note, atleast v2+ needed for this class to work properly, may also need to get from cdn using easy_install

'''
This file contains all the functions and classes needed
in order to run a basic API, with
create, read, delete, and edit functionality for items 
within a table in mysql.
'''

#aquire either all entries of database, or information for a single one
def get_device2(db, nid, tname, fields):
	cursor = db.cursor(dictionary=True)
	status = 204

	if nid == None:
		query = "SELECT "
		for key in fields:
			query = query+key+", "
		query = query[:-2]
		query = query+" FROM "+tname+" ORDER BY id;"
		cursor.execute(query)
	else:
		cursor.execute('select * from ' + tname + ' where id=%s', (nid,))
	recs = []
	rec = {'id': 0, 'pid' : 'Fail'}

	for row in cursor:
		for key in row.keys():
			if key in fields:
				item = str(row[key])
				if item[:9] == "bytearray":  #updated mysql connector module makes this necassary 
					item = item[item.find("\'")+1:]
					item = item[:item.find("\'")]
				fields[key] = item
			rec = fields 
			status = 200
		recs.append(rec.copy())
	cursor.close()
	if nid == None:
		return simplejson.dumps(recs), status
	else:
		return simplejson.dumps(rec), status

def get_range(db,beg,end,tname,fields):
	cursor = db.cursor(dictionary=True)
	
	#building query	
	query = "SELECT "
	for key in fields:
		query = query+key+", "
	query = query[:-2]
	query = query+" FROM "+tname+" WHERE id between " + str(beg) + " AND " + str(end) + " ORDER BY id;"
	print(query)
	cursor.execute(query)
	
	recs = []
	for row in cursor:
		for key in row.keys():
			if key in fields:
				item = str(row[key])
				if item[:9] == "bytearray":  #updated mysql connector module makes this necassary 
					item = item[item.find("\'")+1:]
					item = item[:item.find("\'")]
				fields[key] = item
			rec = fields 
		recs.append(rec.copy())
	cursor.close()
	
	status = 200
	return simplejson.dumps(recs), status

#
#Get records based off a starting record, and desired count
#
def get_count_forward(db,start,count,tname,fields):
	cursor = db.cursor(dictionary=True)
	
	#building query	
	query = "SELECT "
	for key in fields:
		query = query+key+", "
	query = query[:-2]
	query = query+" FROM "+tname+" WHERE id > " + str(start) + " LIMIT " + str(count)
	print(query)
	cursor.execute(query)
	
	recs = []
	for row in cursor:
		for key in row.keys():
			if key in fields:
				item = str(row[key])
				if item[:9] == "bytearray":  #updated mysql connector module makes this necassary 
					item = item[item.find("\'")+1:]
					item = item[:item.find("\'")]
				fields[key] = item
			rec = fields 
		recs.append(rec.copy())
	cursor.close()
	
	status = 200
	return simplejson.dumps(recs), status

def get_count_back(db,start,count,tname,fields):
	cursor = db.cursor(dictionary=True)
	
	#building query	
	query = "SELECT * FROM (SELECT "
	for key in fields:
		query = query+key+", "
	query = query[:-2]
	query = query + " FROM " + tname + " WHERE id < " + str(start) + " ORDER BY id DESC LIMIT " + str(count) + ") AS id ORDER BY id ASC;"
	print(query)
	cursor.execute(query)
	
	recs = []
	for row in cursor:
		for key in row.keys():
			if key in fields:
				item = str(row[key])
				if item[:9] == "bytearray":  #updated mysql connector module makes this necassary 
					item = item[item.find("\'")+1:]
					item = item[:item.find("\'")]
				fields[key] = item
			rec = fields 
		recs.append(rec.copy())
	cursor.close()
	
	status = 200
	return simplejson.dumps(recs), status

def getSpecItem(db,col,desItem,tname,fields):
	cursor = db.cursor(dictionary=True)
	
	#building query	
	query = "SELECT "
	for key in fields:
		query = query+key+", "
	query = query[:-2]
	query = query+" FROM " + tname + " WHERE " + col + " = \"" + desItem + "\""
	print(query)
	cursor.execute(query)
	
	recs = []
	for row in cursor:
		for key in row.keys():
			if key in fields:
				item = str(row[key])
				if item[:9] == "bytearray":  #updated mysql connector module makes this necassary 
					item = item[item.find("\'")+1:]
					item = item[:item.find("\'")]
				fields[key] = item
			rec = fields 
		recs.append(rec.copy())
	cursor.close()

	status = 200
	return simplejson.dumps(recs), status

#
# Delete a single record
#
def delete_record(db, nid, tname):
	cursor = db.cursor()
	cursor.execute("delete from " + tname +  " where id=%s", (nid,))
	rows = cursor.rowcount
	cursor.close()
	if rows == 1:
		return 200
	else:
		return 204

#update a record in the database
def update_record(db, nid, content, fields, tname):
	if(content):
		upd = "UPDATE " + tname + " SET "
		for key in content:
			if key in fields:
				if content.get(key) != None:
					upd = upd+key+"=\'"+str(content.get(key))+"\', "
		upd = upd[:-2]
		upd = upd+" WHERE id="+str(nid)+";"
		print(upd)

	cursor = db.cursor()
	try:
		cursor.execute(upd)
		cursor.close()
		return simplejson.dumps({"id":nid}),200
	except:
		cursor.close()
		return simplejson.dumps({"id" : 0}),204
    

#create a new record in the database
def create_record(db, content, fields, tname):
	if(content):
		new = "INSERT INTO " + tname + " ("
		for key in content:
			if key in fields and key != "id":
				if content.get(key) != None:
					new = new + key + ", "
		new = new[:-2]
		new = new + ") VALUES ("
		for key in content:
			if key in fields and key != "id":
				if content.get(key) != None:
					new = new + "\'" + str(content.get(key))+"\', "
		new = new[:-2]
		new = new + ");"
		print(new)

	cursor = db.cursor()
	try:
		cursor.execute(new)
		id = cursor.lastrowid
		cursor.close()
		return simplejson.dumps({"id": id}), 200
	except:
		cursor.close()
		return simplejson.dumps({"id" : 0}), 204

#called by routeMaker class, does the routing for a given
#dataModel object
def defineBlueprint(name,use,keys):
	base = Blueprint(name,__name__,url_prefix="/base")
	@base.route('/', methods=['GET', 'POST'])
	def noSpec():
		sentKey = request.headers.get('key')
		if not keys or sentKey in keys.values():
			if request.method == 'GET':
				js, status = get_device2(use.db, None, use.tableName, use.fields)
				return Response(js, mimetype="application/json"), status
			elif request.method == 'POST':
				content = request.json
				js, status = create_record(use.db, content, use.fields, use.tableName)
				return Response(js, mimetype="application/json"), status
			else:
				return "Unknown type"
		else:
			return "Invalid api key sent \"" + str(sentKey) + "\"",401
	@base.route('/<int:post_id>', methods=['GET', 'PUT', 'DELETE'])
	def spec(post_id):
		sentKey = request.headers.get('key')
		if not keys or sentKey in keys.values():
			if request.method == 'GET':
				js, status = get_device2(use.db, post_id, use.tableName, use.fields)
				return Response(js, mimetype="application/json"), status
			elif request.method == 'PUT':
				content = request.json
				js, status = update_record(use.db, post_id, content, use.fields, use.tableName)
				return Response(js, mimetype="application/json"), status
			elif request.method == 'DELETE':
				status = delete_record(use.db, post_id, use.tableName)
				return "", status
			else:
				return "Got an unknown method id=%d" % post_id
		else:
			return "Invalid api key sent \"" + str(sentKey) + "\"",401
	@base.route('/RANGESEARCH/<int:beg_search>/<int:end_search>', methods=['GET'])
	def getRange(beg_search,end_search):
		sentKey = request.headers.get('key')
		if not keys or sentKey in keys.values():
			if request.method == 'GET':
				if beg_search < end_search and beg_search > 0:
					js, status = get_range(use.db,beg_search,end_search,use.tableName,use.fields)
					return Response(js, mimetype="application/json"), status
				else:
					return "Invalid Range"
			else:
				return "Got an unknown method"
		else:
			return "Invalid api key sent \"" + str(sentKey) + "\"",401
	
	@base.route('/COUNTSEARCHFORWARD/<int:lowestNum>/<int:desired>', methods=['GET'])
	def getCountForward(lowestNum,desired):
		sentKey = request.headers.get('key')
		if not keys or sentKey in keys.values():
			if request.method == 'GET':
				if desired > 0 and lowestNum > 0:
					js, status = get_count_forward(use.db,lowestNum,desired,use.tableName,use.fields)
					return Response(js, mimetype="application/json"), status
				else:
					return "Invalid request paramaters"
			else:
				return "Got an unknown method"
		else:
			return "Invalid api key sent \"" + str(sentKey) + "\"",401

	@base.route('/COUNTSEARCHBACK/<int:lowestNum>/<int:desired>', methods=['GET'])
	def getCountBack(lowestNum,desired):
		sentKey = request.headers.get('key')
		if not keys or sentKey in keys.values():
			if request.method == 'GET':
				if desired > 0 and lowestNum > 0:
					js, status = get_count_back(use.db,lowestNum,desired,use.tableName,use.fields)
					return Response(js, mimetype="application/json"), status
				else:
					return "Invalid request paramaters"
			else:
				return "Got an unknown method"
		else:
			return "Invalid api key sent \"" + str(sentKey) + "\"",401
	@base.route('/NAMESEARCH/<string:colName>/<string:searchTerm>', methods=['GET'])
	def getColItem(colName,searchTerm):
		sentKey = request.headers.get('key')
		if not keys or sentKey in keys.values():
			if request.method == 'GET':
				js, status = getSpecItem(use.db,colName,searchTerm,use.tableName,use.fields)
				return Response(js, mimetype="application/json"), status
			else:
				return "Got an unknown method"
		else:
			return "Invalid api key sent \"" + str(sentKey) + "\"",401
	return base

#Used in order to create objects with associated database information
class dataModel:
	def __init__(self,tableNameG,fieldsG,cfgfileG,sectionG):
		self.tableName = tableNameG
		self.fields = []
		self.fields = fieldsG
		self.cfgfile = cfgfileG
		self.section = sectionG
		self.db = self.dbConnect()
	
	@staticmethod
	def remove_quote(s):
		s = s.strip('\'')
		s = s.strip('\"')
		return s
	
	def dbConnect(self):
		config = configparser.ConfigParser()
		config.read(self.cfgfile)
		mysql_host = self.remove_quote(config.get(self.section, 'mysql_host'))
		mysql_user = self.remove_quote(config.get(self.section, 'mysql_user'))
		mysql_pwd = self.remove_quote(config.get(self.section, 'mysql_pwd'))
		mysql_db = self.remove_quote(config.get(self.section, 'mysql_db'))

		try:
			databaseConnection = mysql.connector.connect(host=mysql_host, user=mysql_user, passwd=mysql_pwd, db=mysql_db, use_unicode=False)
			return databaseConnection
		except:
			print("Error opening database")
			return 0
			sys.exit(1)

#used to set up where to access API (/<something>), doing this by defining 
#where specific queries in mysql should go.
class routeMaker:
	def __init__(self,mod,pName,ap):
		self.model = mod	#db info
		self.pathName = "/" + pName	#pathname api will be accessed from
		self.app = ap	#flask object to access serving features
		#create apiUser key cfg file if one doesnt exist
		self.keys={}	#dictionary to hold users qualified to access api
		self.keyFileName = pName+".cfg"
		if(not os.path.exists(self.keyFileName)):
			self.keyFile = open(self.keyFileName,'w+')
			self.keyFile.write("[users]" + "\n")
			self.keyFile.close()
		else:
			keyConfig = configparser.ConfigParser()
			keyConfig.optionxform=str
			keyConfig.read(self.keyFileName)
			for user in keyConfig.options("users"):
				self.keys[user] = keyConfig.get("users",user)
		#Define how api is to be reached/register path
		self.name = defineBlueprint(self.pathName,self.model,self.keys)
		self.app.register_blueprint(self.name,url_prefix=self.pathName)


	def addUser(self,newApiUser):
		#use newApiUser as key
		#create a random uuid associated with new user
		self.keyFile = open(self.keyFileName,'a+')
		newUser = newApiUser
		apiKey = str(uuid.uuid4())
		#dont want to define new user if already in cfg file
		if newUser not in self.keys:
			self.keys[newUser] = apiKey
			self.keyFile.write(newUser + " = " + apiKey + "\n")
		self.keyFile.close()
