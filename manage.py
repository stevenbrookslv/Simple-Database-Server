#/usr/bin/env python3
#functions for managing permissions on routes

class userManage:
	def __init__(self,routeObject):
		self.routeObj = routeObject

	def delUser(self, userToDelete):
		keyFile = open(self.routeObj.keyFileName,'r+')
		delTemp = ""
		fileStrings = keyFile.readlines()
		for line in fileStrings:
			print(line)
			try:	
				#need this to handle file header
				user,eq,pw = line.split(" ")
				if(userToDelete == user):
					delTemp = line
					break
			except:	
				#just skip this loop
				continue
		keyFile.seek(0)
		for line in fileStrings:
			if delTemp != line:
				keyFile.write(line)
		keyFile.truncate()
		keyFile.close()

	def printUsers(self):
		print(self.routeObj.keys)
	
	def addUser(self,newApiUser,newApiPwd):
		#use newApiUser as username
		#create a salted hash associated with new user password
		keyFile = open(self.routeObj.keyFileName,'a+')
		newUser = newApiUser
		apiKeySalt = uuid.uuid4().hex
		#dont want to define new user if already in cfg file
		if newUser not in self.routeObj.keys:
			apiKey = hashlib.sha512(apiKeySalt.encode() + newApiPwd.encode()).hexdigest() + "-" + apiKeySalt
			self.routeObj.keys[newUser] = apiKey
			keyFile.write(newUser + " = " + apiKey + "\n")
		keyFile.close()
