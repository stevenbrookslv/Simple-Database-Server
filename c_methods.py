#!/usr/bin/env python3
from flask import request, Response, Blueprint, session
from flask.ext.login import LoginManager,login_user,current_user
from flask.ext.security import login_required
import configparser
import hashlib
import uuid
import sqlite3
import re,os,sys
import simplejson
import mysql.connector #note, atleast v2+ needed for this class to work properly, may also need to get from cdn using easy_install

'''
This file contains all the functions and classes needed
in order to run a basic API, with
create, read, delete, and edit functionality for items 
within a table in mysql.
'''

login_manager = LoginManager()

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
	query = "%s FROM %s WHERE id BETWEEN %s AND %s ORDER BY id;" %(query, tname, beg, end)
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
		query = "%s %s, " %(query, key)
	query = query[:-2]
	query = "%s FROM %s WHERE id > %s ORDER BY id LIMIT %s;" %(query, tname, start, count)
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
		query = "%s %s, " %(query, key)
	query = query[:-2]
	query = "%s FROM %s WHERE id < %s ORDER BY id DESC LIMIT %s) AS id ORDER BY id ASC;"  %(query, tname, start, count)
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
		query = "%s %s, " %(query, key)
	query = query[:-2]
	query = "%s FROM %s WHERE %s = \"%s\"" %(query, tname, col, desItem)
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
	cursor.execute("DELETE FROM %s WHERE id=%s" %(tname,nid))
	rows = cursor.rowcount
	cursor.close()
	if rows == 1:
		return 200
	else:
		return 204

#update a record in the database
def update_record(db, nid, content, fields, tname):
	if(content):
		upd = "UPDATE %s SET" %(tname)
		for key in content:
			if key in fields:
				if content.get(key) != None:
					upd = "%s %s=\"%s\"\"," %(upd, key, content.get(key))
		upd = upd[:-2]
		upd = "%s WHERE id=%s;" %(upd, nid)

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
		new = "INSERT INTO %s (" %(tname)
		for key in content:
			if key in fields and key != "id":
				if content.get(key) != None:
					new = "%s %s, " %(new, key)
		new = new[:-2]
		new = "%s) VALUES (" %(new)
		for key in content:
			if key in fields and key != "id":
				if content.get(key) != None:
					new = "%s\"%s\", " %(new,content.get(key))
					#new = new + "\'" + str(content.get(key))+"\', "
		new = new[:-2]
		new = "%s);" %(new)
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

def getMaxId(db, tName):
	query = "SELECT id FROM %s ORDER BY id DESC LIMIT 1;" %(tName)
	#print(query)
	cursor = db.cursor(buffered=True)
	try:	
		cursor.execute(query)
		for row in cursor:
			id = row[0]
		cursor.close()
		return simplejson.dumps({"lastId": id}), 200
	except:
		cursor.close()
		return simplejson.dumps({"lastId": "null"}), 204

def getMinId(db, tName):
	query = "SELECT id FROM %s LIMIT 1;" %(tName)
	print(query)
	cursor = db.cursor(buffered=True)
	try:	
		cursor.execute(query)
		for row in cursor:
			id = row[0]
		cursor.close()
		return simplejson.dumps({"firstId": id}), 200
	except:
		cursor.close()
		return simplejson.dumps({"firstId": "null"}), 204


#called by routeMaker class, does the routing for a given
#dataModel object
def defineBlueprint(robj, name,use):
	base = Blueprint(name,__name__,url_prefix="/base")
	@base.route('/', methods=['GET'])
	def noSpecGet():
		if request.method == 'GET':
			js, status = get_device2(use.db, None, use.tableName, use.fields)
			return Response(js, mimetype="application/json"), status
		else:
			return "Unknown type", 405
	if(robj.secW):
		@base.route('/', methods=['POST'])
		@login_required
		def noSpecPost():
			if(request.method == "POST"):
				content = request.json
				js, status = create_record(use.db, content, use.fields, use.tableName)
				use.db.commit()
				return Response(js, mimetype="application/json"), status
			else:
				return "Unknown type", 405
	else:
		@base.route('/', methods=['POST'])
		def noSpecPost():
			if(request.method == "POST"):
				content = request.json
				js, status = create_record(use.db, content, use.fields, use.tableName)
				use.db.commit()
				return Response(js, mimetype="application/json"), status
			else:
				return "Unknown type", 405

	@base.route('/<int:post_id>', methods=['GET'])
	def spec(post_id):
		if request.method == 'GET':
			js, status = get_device2(use.db, post_id, use.tableName, use.fields)
			return Response(js, mimetype="application/json"), status
		else:
			return "Got an unknown method id=%d" % post_id
	if(robj.secW):
		@base.route('/<int:post_id>', methods=['PUT', 'DELETE'])
		@login_required
		def specPutDel(post_id):
			if request.method == 'PUT':
				content = request.json
				js, status = update_record(use.db, post_id, content, use.fields, use.tableName)
				use.db.commit()
				return Response(js, mimetype="application/json"), status
			elif request.method == 'DELETE':
				status = delete_record(use.db, post_id, use.tableName)
				use.db.commit()
				return "", status
			else:
				return "Got an unknown method id=%d" % post_id
	else:
		@base.route('/<int:post_id>', methods=['PUT', 'DELETE'])
		def specPutDel(post_id):
			if request.method == 'PUT':
				content = request.json
				js, status = update_record(use.db, post_id, content, use.fields, use.tableName)
				use.db.commit()
				return Response(js, mimetype="application/json"), status
			elif request.method == 'DELETE':
				status = delete_record(use.db, post_id, use.tableName)
				use.db.commit()
				return "", status
			else:
				return "Got an unknown method id=%d" % post_id
	@base.route('/MINID', methods=['GET'])
	def minId():
		if request.method == 'GET':
			js, status = getMinId(use.db, use.tableName)
			return Response(js, mimetype="application/json"), status
		else:
			return "Unknown type"
	@base.route('/MAXID', methods=['GET'])
	def maxId():
		if request.method == 'GET':
			js, status = getMaxId(use.db, use.tableName)
			return Response(js, mimetype="application/json"), status
		else:
			return "Unknown type"
	@base.route('/RANGESEARCH/<int:beg_search>/<int:end_search>', methods=['GET'])
	def getRange(beg_search,end_search):
		if request.method == 'GET':
			if beg_search < end_search and beg_search > 0:
				js, status = get_range(use.db,beg_search,end_search,use.tableName,use.fields)
				return Response(js, mimetype="application/json"), status
			else:
				return "Invalid Range"
		else:
			return "Got an unknown method"
	
	@base.route('/COUNTSEARCHFORWARD/<int:lowestNum>/<int:desired>', methods=['GET'])
	def getCountForward(lowestNum,desired):
		if request.method == 'GET':
			if desired > 0 and lowestNum >= 0:
				js, status = get_count_forward(use.db,lowestNum,desired,use.tableName,use.fields)
				return Response(js, mimetype="application/json"), status
			else:
				return "Invalid request paramaters"
		else:
			return "Got an unknown method"

	@base.route('/COUNTSEARCHBACK/<int:lowestNum>/<int:desired>', methods=['GET'])
	def getCountBack(lowestNum,desired):
		if request.method == 'GET':
			if desired > 0 and lowestNum >= 0:
				js, status = get_count_back(use.db,lowestNum,desired,use.tableName,use.fields)
				return Response(js, mimetype="application/json"), status
			else:
				return "Invalid request paramaters"
		else:
			return "Got an unknown method"
	@base.route('/NAMESEARCH/<string:colName>/<string:searchTerm>', methods=['GET'])
	def getColItem(colName,searchTerm):
		if request.method == 'GET':
			js, status = getSpecItem(use.db,colName,searchTerm,use.tableName,use.fields)
			return Response(js, mimetype="application/json"), status
		else:
			return "Got an unknown method"

	@base.route('/login', methods=['POST'])
	def login():
		suc = False
		status = 200
		if(robj.secW):
			try:
				userData = request.json
				if(userData):
					if(robj.checkUser(userData['user'],userData["password"]) != None):
						user = load_user(userData['user'])
						user.setAuth(True)
						login_user(user)
						suc = True
						status = 200
					else:
						suc = False
						status = 401
			except NameError:	#no username and password sent
				suc = False
				status = 401
			return Response(simplejson.dumps({"result": suc}), mimetype="application/json"), status
	@base.route('/logout', methods=['GET'])
	@login_required
	def logout():
		user = current_user
		user.setAuth(False) 
		suc = True
		status = 200
		return Response(simplejson.dumps({"result": suc}), mimetype="application/json"), status

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


#will need a global user database list for now
userdbs = []
#used to set up where to access API (/<something>), doing this by defining 
#where specific queries in mysql should go.
class routeMaker:
	def __init__(self,mod,pName,ap,secureWrites = False):
		self.model = mod	#db info
		self.pathName = "/" + pName	#pathname api will be accessed from
		self.app = ap	#flask object to access serving features
		#create apiUser key cfg file if one doesnt exist
		self.secW = secureWrites
		self.keyFileName = pName+"_userdb"
		userdbs.append(self.keyFileName)
		if(not os.path.exists(self.keyFileName)):
			dbFile = sqlite3.connect(self.keyFileName)
			self.dbFile = dbFile
			cursor = dbFile.cursor()
			cursor.execute("CREATE TABLE users(name TEXT, password TEXT, authenticated INTEGER, active INTEGER)")
			dbFile.commit()		#db connection object makes commits
			dbFile.close()
			cursor.close()
		self.dbFile = sqlite3.connect(self.keyFileName)
		self.cursor = self.dbFile.cursor()
		self.name = defineBlueprint(self, self.pathName,self.model)
		self.app.register_blueprint(self.name,url_prefix=self.pathName)
	
	def checkUser(self, user, pwd):
		que = "SELECT name, password FROM users WHERE name=\"%s\"" %(user)
		dbFile = sqlite3.connect(self.keyFileName)
		cursor = dbFile.cursor()
		cursor.execute(que)
		user = cursor.fetchone()
		try:	
			userPwdStored = user[1]	
			userPwd,userSalt = userPwdStored.split("-")	#getting userPwd after hash, and salt to hash old password
			enteredPwd = hashlib.sha512(userSalt.encode() + pwd.encode()).hexdigest()	#hashing entered password with salt
			if(enteredPwd == userPwd):
				return user
		except:
			return None
	
@login_manager.user_loader
def load_user(user_id):
	que = "SELECT name, authenticated, active FROM users WHERE name=\"%s\"" %(user_id)
	dbFile = sqlite3.connect(userdbs[0])
	cursor = dbFile.cursor()
	cursor.execute(que)
	user = cursor.fetchone()
	try:	
		userName = user[0]
		authed = user[1]
		if(authed == 0):
			authed = False
		else:
			authed = True
		act = user[1]
		if(act == 0):
			act = False
		else:
			act = True
		user = User(userName, authed, act)
		return user
	except:
		return None

class User():
	def __init__(self,uname,authenticated, active):
		self.username = uname
		self.is_authenticated = authenticated
		self.is_active = active
		self.isanonymous = False
		
	def get_id(self):
		return self.username
	
	def is_authenticated(self):
		return self.authenticated

	def is_active(self):
		return self.active

	def is_anonymous(self):
		return False

	def setAuth(self, auth):
		dbFile = sqlite3.connect(userdbs[0])
		cursor = dbFile.cursor()
		if(auth == True):
			que = "UPDATE users SET authenticated=1 WHERE name=\"%s\"" %self.username
		else:
			que = "UPDATE users SET authenticated=0 WHERE name=\"%s\"" %self.username
		cursor.execute(que)
		dbFile.commit()
		
