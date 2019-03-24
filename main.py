import sys
import os
import shutil
import logging
import csv
import mysql.connector
import hashlib
import time
import datetime

def fileCopy(src_files,src,dst):
	for file_name in src_files:
		full_file_name = os.path.join(src, file_name)
		if (os.path.isfile(full_file_name)):
			shutil.copy(full_file_name, dest)

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
	fileList = os.listdir("/home/luis/onebackend/incoming")
	return fileList

def loadInfo(filePath):
	with open(filePath, 'rb') as csvfile:
		csvReader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_MINIMAL)
	        logging.debug("Reading from file " + filePath)
		conn = mysql.connector.connect(host='localhost', port=3306,user='onebackend', password='password',database='onebackenddb')
	        cursor = conn.cursor()
		for row in csvReader:
			logging.debug("Inserting data for row "+str(row))
			size=os.stat("/home/luis/onebackend/incoming/"+row[2]).st_size
			md5=md5sum("/home/luis/onebackend/incoming/"+row[2])
			md5="adfbadfklaj18612"
			creationDate=datetime.datetime.fromtimestamp(os.path.getmtime("/home/luis/onebackend/incoming/"+row[2])).strftime('%Y-%m-%d %H-%M-%S')
			copyDate=time.strftime('%Y-%m-%d %H-%M-%S')
                        extension=row[2].split(".")[-1]
		        sql_insert_query = """ INSERT INTO cases (caseName,evidenceAlias,size,fileName,md5,creationDate,copyDate,extension) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
			insert_tuple = (row[0], row[1],size,row[2],md5,creationDate,copyDate,extension)
			result  = cursor.execute(sql_insert_query, insert_tuple)
			conn.commit()
			logging.debug("Inserted data for row "+str(row))
			insertRowinFile(row,"/home/luis/onebackend/basededatos.txt")

def main():
        logging.basicConfig(filename='logging.log',level=logging.DEBUG)
        logging.debug('Execution begin')
	if sys.argv[1]=="list":
		print listFolder()
	elif sys.argv[1]=="load":
		loadInfo(sys.argv[2])
	elif sys.argv[1]=="dump":
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
	elif sys.argv[1]=="mmls":
#		print sys.argv

if __name__== "__main__":
	main()
