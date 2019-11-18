#!/bin/bash

##
#Script to run a RDF2Graph
#

#Settings
export rdf2graph=/data/RDF2Graph

#Input Parameters
database_file_name=$1;		#<rdfFolderPath,classPropertyFilepath>
graph_folder_name=$2;      # folder which contains vertex edge format representations of RDF data. This format is input to the gSpan Algorithm
RESULT_folder=$3;        #Folder name where the execution time will be stored


while IFS=$';' read -r col1 col2 col3 
do 
    python3.6 $rdf2graph/main.py $col1 $col2 $col3 $graph_folder_name $RESULT_folder
done <$database_file_name
