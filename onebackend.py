import sys
import os
import shutil
import logging
import csv
#import mysql.connector
import hashlib
import time
import datetime

srcFolder = "/root/prueba/incoming/"
databaseFile = "basededatos.txt"

def md5sum(filename, blocksize=65536):
	hash = hashlib.md5()
	with open(filename, "rb") as f:
		for block in iter(lambda: f.read(blocksize), b""):
			hash.update(block)
	return hash.hexdigest()

def insertRowinFile(row,fileName):
	with open(fileName, 'ab') as csvfile:
		csvWriter = csv.writer(csvfile, delimiter='|',quotechar='"',quoting=csv.QUOTE_MINIMAL)
                csvWriter.writerow([unicode(col) for col in row])
		logging.debug("Row inserted in file "+str(fileName)+" "+str(row))

def databaseDataCollect():
	conn = mysql.connector.connect(host='localhost', port=3306,user='onebackend', password='password',database='onebackenddb')
	crsr = conn.cursor()
	crsr.execute("SELECT * FROM cases")
	results = crsr.fetchall()
	return results

def listFolder():
	fileList = os.listdir(srcFolder)
	return fileList

def loadInfo(filePath):
	with open(filePath, 'rb') as csvfile:
		csvReader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_MINIMAL)
	        logging.debug("Reading from file " + filePath)
		conn = mysql.connector.connect(host='localhost', port=3306,user='onebackend', password='password',database='onebackenddb')
	        cursor = conn.cursor()
		for row in csvReader:
			logging.debug("Inserting data for row "+str(row))
			size=os.stat(srcFolder+row[2]).st_size
			md5=md5sum(srcFolder+row[2])
			creationDate=datetime.datetime.fromtimestamp(os.path.getmtime(srcFolder+row[2])).strftime('%Y-%m-%d %H-%M-%S')
			copyDate=time.strftime('%Y-%m-%d %H-%M-%S')
                        extension=row[2].split(".")[-1]
		        sql_insert_query = """ INSERT INTO cases (caseName,evidenceAlias,size,fileName,md5,creationDate,copyDate,extension) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
			insert_tuple = (row[0], row[1],size,row[2],md5,creationDate,copyDate,extension)
			result  = cursor.execute(sql_insert_query, insert_tuple)
			conn.commit()
			logging.debug("Inserted data for row "+str(row))
			insertRowinFile(row,"/home/luis/onebackend/basededatos.txt")

def copyData(destFolder):
	src_files = os.listdir(srcFolder)
	for file_name in src_files:
		full_file_name = os.path.join(srcFolder, file_name)
		if (os.path.isfile(full_file_name)):
			shutil.copy(full_file_name, destFolder)

def status():
	src_files=os.listdir(srcFolder)
	ingestedFiles=[]
	with open(databaseFile, 'rb') as csvfile:
		csvReader = csv.reader(csvfile, delimiter='|',quotechar='"',quoting=csv.QUOTE_MINIMAL)
		for row in csvReader:
			if str(row[4]) in src_files:
				print row

def main():
        logging.basicConfig(filename='logging.log',level=logging.DEBUG)
        logging.debug('Execution begin')
	if len(sys.argv)>1:
		if sys.argv[1]=="list":
			logging.debug("Listing incoming folder")
			for file in listFolder():
				print file
			logging.debug("Listing incoming folder finished")
		elif sys.argv[1]=="copy":
			logging.debug("Copying info to: "+sys.argv[2])
			copyData(sys.argv[2])
			logging.debug("Copying info finished")
		elif sys.argv[1]=="load":
		        logging.debug("Loading info from file: "+sys.argv[2])
			loadInfo(sys.argv[2])
		        logging.debug("Loading info finished")
		elif sys.argv[1]=="status":
                        logging.debug("Status requested")
			status()
                        logging.debug("Status finished")
		elif sys.argv[1]=="dump":
			logging.debug("Databse dump requested")
			cursor=databaseDataCollect()
			try:
			#attempt to read from the file
				file = open(sys.argv[2], 'r')
				file.close()
			except IOError:
			#If it does not exist we create the file
				file = open(sys.argv[2], 'w')
				file.close()
			for row in cursor:
				insertRowinFile(row,sys.argv[2])
		        logging.debug("Database dump finished")
		elif sys.argv[1]=="mmls":
		        logging.debug("MMLS command requested")
			command=""
			for word in sys.argv[1:]:
				command+=command+" "+word
			os.system(command)
			logging.debug("MMLS command finished")
	else:
		print("Options not found. Please use one of the following")
		print("> list --> list incoming folder")
		print("> load filename --> load new evidences")
		print("> copy destFolder --> Copy everything from incoming folder to destFolder")
		print("> mmls [-t mmtype ] [-o offset ] [ -i imgtype ] [-b dev_sector_size] [-BrvV] [-aAmM] image [images] --> Execute mmls command")
		print("> dump filename --> export databse to specified file")

if __name__== "__main__":
	main()
