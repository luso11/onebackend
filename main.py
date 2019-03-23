import sys
import os
import shutil
import logging
import csv
import mysql.connector

def copiadatos(src_files,src,dst):
	for file_name in src_files:
		full_file_name = os.path.join(src, file_name)
		if (os.path.isfile(full_file_name)):
			shutil.copy(full_file_name, dest)

def recuperaDatos():
	conn = mysql.connector.connect(host='localhost', port=3306,user='onebackend', password='password',database='onebackenddb')
	crsr = conn.cursor()
	crsr.execute("SELECT * FROM casos")
	resultados = crsr.fetchall()
	return resultados

def listaCarpeta():
	src = "/home/luis/onebackend/incoming"
	listado = os.listdir(src)
	return listado

def main():
	funcion = sys.argv[1]
        logging.basicConfig(filename='logging.log',level=logging.DEBUG)
        logging.debug('Iniciamos ejecucion')
	if funcion=="list":
		print listaCarpeta()
	else:
		cursor=recuperaDatos()
		try:
			with open(r'/home/luis/onebackend/basededatos.txt', 'wb') as csvfile:
				csvWriter = csv.writer(csvfile, delimiter='|',quotechar='"',quoting=csv.QUOTE_MINIMAL)
				for row in cursor:
					csvWriter.writerow([unicode(col) for col in row])
					print unicode(col)
		except:
			logging.debug('Cannot open text file')

if __name__== "__main__":
	main()
