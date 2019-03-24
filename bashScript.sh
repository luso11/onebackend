#!/bin/sh
user=$(whoami)
group=$(groups)

for folder in "$@"
do
	directories=$(ls -l $folder | grep ^d | awk -v user="$user" -v group="$group"\
	'($3==user && match($1,/^.r.x/)) || ($4==group && match($1,/^....r.x/)) || match($1,/^.......r.x/) {print $9}')
	echo "Already have permissions on: " $directories
	lista=[]
	for subdirectory in $directories
	do
		subdirectoriesAndFiles=$(ls -l $folder/$subdirectory | awk -v user="$user" -v group="$group" \
		'($3==user && match($1,/^.r.x/)) || ($4==group && match($1,/^....r.x/)) || match($1,/^.......r.x/) {print $9}')
	done
	echo "Already have permissions on these subdirectories and files: " $subdirectoriesAndFiles
	files=$(ls -l $folder | grep -v ^d | awk -v user="$user" -v group="$group"\
        '!($3==user && match($1,/^.r.x/)) && !($4==group && match($1,/^....r.x/)) && !match($1,/^.......r.x/) {print $9}')
	for file in $files
	do
		 chmod u+rx $folder/$file
	done

done
