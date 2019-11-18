#!/bin/bash

##
#Script to run Frequent Star Patterns Detection
#

#Settings
export fsgp=/data/GFSP/

#Input Parameters
database_file_name=$1 ;        #path where the database is located
frequent_stars_folder=$2;    #Path where the benchmark of queries is located
RESULT_folder=$3;        #Filename where the query output will be stored
json_folder=$4;		# Folder where json file containing class and properties involved in frequent star patterns will be written


while IFS=$';' read -r col1 col2 col3
do 
    python3.6 $fsgp/main.py $col1 $col2 $frequent_stars_folder $RESULT_folder $col3 $json_folder -s 1
done <$database_file_name

