# Graph-Factorization
Graph Factorization project creates compact representations of RDF graphs by reducing the number of frequent star patterns (FSP) in the RDF graphs. In factorized representations of RDF graphs the number of RDF triples is reduced while preserving the knowledge encoded in the data. Graph factorization project requires a class and a set of corresponding properties, involved in frequent star patterns, to perform factorization. *EFSP* and *GFSP* perform FSP detection by identifying classes and properties involved in frequent star patterns. The source code of factorization, EFSP, and GFSP are provided along with an example of sensor data containing temperature observations from [LinkedSensorData](http://wiki.knoesis.org/index.php/LinkedSensorData). 

Running this project requires following steps:

1.  Configuration
2.  FSP Detection
3.  Factorization

# 1.  Configuration
In this step a docker image of ubuntu is created, and ubuntu image along with an other docker container running virtuoso endpoint are started using docker-compose.
```
$cd Graph-Factorization
$docker build -t ubuntu1804 .
$docker-compose up -d
$docker exec -it graphFactorization bash
```

# 2.  FSP Detection
Two approached *EFSP* and *GFSP* are provided to detect frequent star patterns. Each approach is explined below long with its usage.

## 2.1 EFSP
*EFSP* performs an exhaustive search over the frequent subgraphs identified by a graph mining algorithm. We have implemented *EFSP*, which uses [gSpan](https://github.com/betterenvi/gSpan) as baseline. Running *EFSP* involves following steps:

### Step 1. Running RDF2Graph
[gSpan](https://github.com/betterenvi/gSpan) requires a graph format with vertices(v) and edges(e), therefore, RDF2Graph converts RDF graphs to the required graph format. Given below is the command to run RDF2Graph.
```
$python3 main.py $path_to_RDF $RDF_format $path_to_class_property_file $path_to_ve_graph_folder $path_to_folder_to_save_exe_parameters
```
#### Parameters
$path_to_RDF - It is the path to folder containing RDF data.

$RDF_format - It is a strinng mentioning the input format of RDf data.

$path_to_class_property_file - Path to the file containg a class and the properties of the class to be checked for FSP.

$path_to_ve_graph_folder - Path to a output folder to save the ve graph format of the RDF data.

$path_to_folder_to_save_exe_parameters - Path to a folder to save the execution time and other parameters observed during execution.

#### Running RDF2Graph using Example
```
$cd RDF2Graph
$python3 main.py /data/database/RDFOriginal/ n3 /data/database/classProperties/Temperatureproperties /data/database/veGraph/  /data/database/Result/
```
Running using shell script.
```
$sh scripts/runRDF2Graph.sh /data/database/db/rdf2graph /data/database/veGraph/ /data/database/Result/
```
### Step 2. Running EFSP
Command to run *EFSP*
```
$python3 main.py -s 1 -d True $path_to_veGraph_file $path_to_folder_to_save_freq_star_patterns $path_to_folder_to_save_exe_parameters $path_to_file_containing_total_class_instances $path_to_class_property_file $path_to_folder_to_store_identified_class_properties
```
#### Parameters

$path_to_veGraph_file - Path to file containing ve graph representations.

$path_to_folder_to_save_freq_star_patterns - Path to folder to save frequent star patterns

$path_to_folder_to_save_exe_parameters - Path to a folder to save the execution time and other parameters observed during execution.

$path_to_file_containing_total_class_instances - Path to file containing total class instances.

$path_to_class_property_file - Path to the file containg a class and the properties of the class to be checked for FSP.

$path_to_folder_to_store_identified_class_properties - Path to folder to store class and properties, in json format, identified by *EFSP*.

#### Running *EFSP* using Example
```
$cd EFSP
$python3 main.py -s 1 -d True /data/database/veGraph/TemperatureObservationgraph.data /data/database/frequentStars/ /data/database/Result /data/database/instances/TemperatureObservation /data/database/classProperties/Temperatureproperties /data/database/json-file/
```
Running using shell script.
```
$sh scripts/runEFSP.sh /data/database/db/efsp /data/database/frequentStars/ /data/database/Result/ /data/database/json-file/
```

## 2.1 GFSP
*GFSP* adopts a Greedy approach to identify properties involved in frequent star patterns. Running *GFSP* involves following steps:

### Step 1. Running GroupBy
*GFSP* requires a list of star patterns in RDF graphs, and corresponding multiplicities, therefore, GroupBy extracts lists of stars by running GroupBy queries over a virtuoso endpoint containing RDF data.  Given below is the command to run GroupBy.
```
$python3 main.py $sparql_endpoint $path_to_class_property_file $path_to_folder_to_store_starList $path_to_folder_to_store_total_class_instances $path_to_folder_to_save_exe_parameters
```

#### Parameters
$sparql_endpoint - SPARQL endoint URL

$path_to_class_property_file - Path to the file containg a class and the properties of the class to be checked for star patterns.

$path_to_folder_to_store_starList - Path to folder to store star lists.

$path_to_folder_to_store_total_class_instances - Path to folder to store total class instances.

$path_to_folder_to_save_exe_parameters - Path to a folder to save the execution time and other parameters observed during execution.

#### Running GroupBy using Example
```
$cd GroupBy
$python3 main.py http://virtuosoGraphF:8890/sparql /data/database/classProperties/Temperatureproperties /data/database/starList /data/database/instances /data/database/Result/
```
Running using shell script.
```
sh scripts/runGroupBy.sh /data/database/db/groupBy /data/database/starList/ /data/database/instances/ /data/database/Result/
```
### Step 2. Running GFSP
Command to run *GFSP*
```
python3 main.py $path_to_file_containing_starLists $path_to_class_property_file $path_to_folder_to_save_freq_star_patterns $path_to_folder_to_save_exe_parameters $path_to_file_containing_total_class_instances $path_to_folder_to_store_identified_class_properties -s 1
```
#### Parameters

$path_to_file_containing_starLists - Path to file containing star lists.

$path_to_class_property_file - Path to the file containg a class and the properties of the class to be checked for FSP.

$path_to_folder_to_save_freq_star_patterns - Path to folder to save frequent star patterns

$path_to_folder_to_save_exe_parameters - Path to a folder to save the execution time and other parameters observed during execution.

$path_to_file_containing_total_class_instances - Path to file containing total class instances.

$path_to_folder_to_store_identified_class_properties - Path to folder to store class and properties, in json format, identified by *GFSP*.

#### Running *GFSP* using Example
```
$cd GFSP
$python3 main.py /data/database/starList/TemperatureObservation /data/database/classProperties/Temperatureproperties /data/database/frequentStars /data/database/Result /data/database/instances/TemperatureObservation /data/database/json-file/ -s 1
```
Running using shell script.
```
$sh scripts/runGFSP.sh /data/database/db/gfsp /data/database/frequentStars/  /data/database/Result/ /data/database/json-file/
```

# 3. Factorization

## Create Maven Package

```
$mvn package

```

## Run Factorization

```
$java -jar target/RDFFactorization-0.0.1-SNAPSHOT.jar $path_to_json_file $path_to_input_RDF $path_to_output_RDF $RDF_format
```
### Parameters
$path_to_json_file - Path to json file containing a class and corresponding properties to perform factorization. An example of json file is provided in *database/json-file* folder.

$path_to_input_RDF - Path to the folder conataining original RDF to be factorized. An example of original RDF data is provided in *database/input* folder.

$path_to_output_RDF - Path to the folder to save the factorized RDF data. 

$RDF_format - Format of RDF files.

### Running Factorization using Example

Example json file and original RDF data are provided in the *database* folder. Use the command below to run the example.

```
$cd RDFFactorization
$java -jar target/RDFFactorization-0.0.1-SNAPSHOT.jar /data/database/json-file/TemperatureObservation /data/database/RDFOriginal/ /data/database/RDFFactorized/ NTriples
```
