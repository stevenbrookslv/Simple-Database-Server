#/usr/bin/env python3
#functions for managing permissions on routes
import uuid
import hashlib
import sqlite3

class userManage:
	def __init__(self,routeObject):
		self.routeObj = routeObject

	def delUser(self, userToDelete):
		#deletes a user
		cursor = self.routeObj.dbFile.cursor()
		que = "DELETE FROM users WHERE name=\"" + userToDelete + "\""
		cursor.execute(que)
		self.routeObj.dbFile.commit()
		cursor.close()

	def printUsers(self):
		cursor = self.routeObj.dbFile.cursor()
		cursor.execute("SELECT * FROM users")
		iterUsers = cursor.fetchall()
		for row in iterUsers:
			print(row)
		cursor.close()

	def addUser(self,newApiUser,newApiPwd):
		#use newApiUser as username
		#create a salted hash associated with new user password
		cursor = self.routeObj.dbFile.cursor()
		newUser = newApiUser
		que = "SELECT name FROM users WHERE name=\"" + newUser + "\""
		cursor.execute(que)
		test = cursor.fetchone();
		if(test == None):
			apiKeySalt = uuid.uuid4().hex
			#dont want to define new user if already in cfg file
			apiKey = hashlib.sha512(apiKeySalt.encode() + newApiPwd.encode()).hexdigest() + "-" + apiKeySalt
			useUpdQue = "INSERT INTO users VALUES(\"" + newApiUser + "\", \"" + apiKey + "\", 0, 1)"
			cursor.execute(useUpdQue)
			self.routeObj.dbFile.commit()
