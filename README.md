# Simple-Database-Server

# Not currently working on this, while it is good for a very simple backend, and probably has some potential with lots of work, have too much going on and more interesting projects to work on at the moment. 

All that is needed to set up a simple backend for any mysql database is a dictionary with the columns of the database, example-
fields = {
	'id': None,
	'date_posted': None,
	'title': None,
	'prtext': None,
}

Following this, a database object with the title of the database, a path to a config file with database login information, and
the header in the database config file is needed, as follows-
<database object> = dataModel("<table name>",fields,"<Config file with information for database.cfg","<Heading for config file")

example config file-
[whatever title you want]
mysql_host = localhost
mysql_user = mysql user name
mysql_pwd = password for mysql user
mysql_db = name of database that program should use

The last thing that is needed from this point is an object that defines the first part of the url. This takes the database 
object previously created, the desired route, and the app object (with default name of "app") as arguments. Example - 
<route object> = routeMaker(<database object,"<desired route",app)
