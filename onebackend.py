import sys
import os
import shutil
import logging
import csv
import mysql.connector
import hashlib
import time
import datetime

srcFolder = "/home/luis/onebackend/incoming/"
databaseFile = "basededatos.txt"

def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('logging.log', mode='a')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


def md5sum(filename, blocksize=65536):
	hash = hashlib.md5()
	with open(filename, "rb") as f:
		for block in iter(lambda: f.read(blocksize), b""):
			hash.update(block)
	return hash.hexdigest()

def insertRowinFile(row,fileName):
	try:
		with open(fileName, 'ab') as csvfile:
			csvWriter = csv.writer(csvfile, delimiter='|',quotechar='"',quoting=csv.QUOTE_MINIMAL)
                	csvWriter.writerow([unicode(col) for col in row])
			logger.debug("Row inserted in file "+str(fileName)+" "+str(row))
	except:
		logger.debug("Coudln't open "+fileName)

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
	try:
		dest_files = os.listdir(destFolder)
		src_files = os.listdir(srcFolder)
		for file_name in src_files:
			if file_name not in dest_files:
				full_file_name = os.path.join(srcFolder, file_name)
				if (os.path.isfile(full_file_name)):
					shutil.copy(full_file_name, destFolder)
	except:
		print "Cannot copy to "+destFolder
		logger.debug("Cannot copy to "+destFolder)

def status():
	src_files=os.listdir(srcFolder)
	ingestedFiles=[]
	try:
		with open(databaseFile, 'rb') as csvfile:
			csvReader = csv.reader(csvfile, delimiter='|',quotechar='"',quoting=csv.QUOTE_MINIMAL)
			for row in csvReader:
				ingestedFiles.append(row[4])
	except:
		logger.debug('Cannot open file. Ussing empty value for ingestedFiles')
	for file in src_files:
		if file in ingestedFiles:
			print "Processed: " + str(file)
		else:
			print "Missing: " + str(file)

def main():
        logger = setup_custom_logger('onebackend')
	try:
		if len(sys.argv)>1:
			if sys.argv[1]=="list":
				logger.debug("Listing incoming folder")
				for file in listFolder():
					print file
				logger.debug("Listing incoming folder finished")
			elif sys.argv[1]=="copy":
				logger.debug("Copying info to: "+sys.argv[2])
				copyData(sys.argv[2])
				logger.debug("Copying info finished")
			elif sys.argv[1]=="load":
			        logger.debug("Loading info from file: "+sys.argv[2])
				loadInfo(sys.argv[2])
			        logger.debug("Loading info finished")
			elif sys.argv[1]=="status":
                	        logger.debug("Status requested")
				status()
	                        logger.debug("Status finished")
			elif sys.argv[1]=="dump":
				logger.debug("Databse dump requested")
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
			        logger.debug("Database dump finished")
			elif sys.argv[1]=="mmls":
			        logger.debug("MMLS command requested")
				command=""
				for word in sys.argv[1:]:
					command+=command+" "+word
				os.system(command)
				logger.debug("MMLS command finished")
		else:
			print("Options not found. Please use one of the following")
			print("> list --> list incoming folder")
			print("> status --> importing status")
			print("> load filename --> load new evidences")
			print("> copy destFolder --> Copy everything from incoming folder to destFolder")
			print("> mmls [-t mmtype ] [-o offset ] [ -i imgtype ] [-b dev_sector_size] [-BrvV] [-aAmM] image [images] --> Execute mmls command")
			print("> dump filename --> export databse to specified file")
	except:
		logger.debug("Couldn't initiate application")

if __name__== "__main__":
	main()
