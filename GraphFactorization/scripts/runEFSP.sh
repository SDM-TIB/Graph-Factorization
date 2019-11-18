#!/bin/bash

##
#Script to run a RDF2Graph
#

#Settings
export efsp=/data/EFSP/gspan_mining

#Input Parameters
database_file_name=$1;        #path where the database is located
frequent_stars_folder=$2;    #Path where the benchmark of queries is located
RESULT_folder=$3;        #Filename where the query output will be stored
json_folder=$4;		# Folder where json file containing class and properties involved in frequent star patterns will be written

while IFS=$';' read -r col1 col2 col3
do 
    python3.6 $efsp/main.py -s 1 -d True $col1 $frequent_stars_folder $RESULT_folder $col2 $col3 $json_folder
done <$database_file_name

