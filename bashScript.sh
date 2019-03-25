#!/bin/sh
user=$(whoami)
group=$(groups)

for folder in "$@"
do
        echo "Already have permissions on these directories: "
        directories=$(ls -l $folder | grep ^d | awk -v user="$user" -v group="$group"\
        '($3==user && match($1,/^.r.x/)) || ($4==group && match($1,/^....r.x/)) || match($1,/^.......r.x/) {print $9}')
        echo $directories
        echo "Already have permissions on these subdirectories and files: "
        for subdirectory in $directories
        do
                echo "Directory: " $subdirectory
                echo "File: " $(ls -l $folder/$subdirectory | awk -v user="$user" -v group="$group" \
                '($3==user && match($1,/^.r.x/)) || ($4==group && match($1,/^....r.x/)) || match($1,/^.......r.x/) {print $9}')
        done
        files=$(ls -l $folder | grep -v ^d | awk -v user="$user" -v group="$group"\
        '!($3==user && match($1,/^.r.x/)) && !($4==group && match($1,/^....r.x/)) && !match($1,/^.......r.x/) {print $9}')
        for file in $files
        do
                echo "Changing permissions to file: " $folder$file
                sudo chmod +rx $folder/$file
        done

done
