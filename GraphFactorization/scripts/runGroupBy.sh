#!/bin/bash

##
#Script to run GroupBy
#

#Settings
export groupBy=/data/GroupBy

database_file_name=$1		#<endPointURLFilepath;classPropertyFilepath>
starList_folder=$2		#folder to save extracted stars and corresponding multiplicities using group by
instances_folder=$3             # folder where total number of a class instances are written to a file 
RESULT_folder=$4;        #Filename where the execution parameters will be stored

while IFS=$';' read -r col1 col2
do 
    python3.6 $groupBy/main.py $col1 $col2 $starList_folder $instances_folder $RESULT_folder
done <$database_file_name



