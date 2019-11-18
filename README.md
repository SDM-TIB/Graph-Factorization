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

## EFSP
This approach performs an exhaustive search over the frequent subgraphs identified by a graph mining algorithm. We have implemented *EFSP*, which uses [gSpan](https://github.com/betterenvi/gSpan) as baseline. Running *EFSP* involves following steps:

a. Running RDF2Graph
gSpan requires a graph format with vertices(v) and edges(e), therefore, RDF2Graph converts RDF graphs to the required graph format. 
```
$python3 main.py $path_to_RDF $RDF_format $path_to_class_property_file $path_to_ve_graph_folder $path_to_folder_to_save_exe_time
```
#### Parameters
$path_to_RDF - It is the path to folder containing RDF data.
$RDF_format - It is a strinng mentioning the input format of RDf data.
$path_to_class_property_file - Path to the file containg a class and the properties of the class to be checked for FSP.
$path_to_ve_graph_folder - Path to a output folder to save the ve graph format of the RDF data.
$path_to_folder_to_save_exe_time - Path to a folder to save the execution time and other parameters observed during execution.

#### Running Example using RDF2Graph
```
$cd RDF2Graph
$python3 main.py /data/database/RDFOriginal/ n3 /data/database/classProperties/Temperatureproperties /data/database/veGraph/  /data/database/Result/
```
Running using shell script.
```
$sh scripts/runRDF2Graph.sh /data/database/db/rdf2graph /data/database/veGraph/ /data/database/Result/
```



## Create Maven Package

```
$mvn package

```

## Run Factorization

```
$java -jar target/RDFFactorization-0.0.1-SNAPSHOT.jar path_to_json_file path_to_input_RDF path_to_output_RDF
```
### Parameters
* path_to_json_file - Path to json file containing a class and corresponding properties to perform factorization. An example of json file is provided in *database/json-file* folder.
* path_to_input_RDF - Path to the folder conataining original RDF to be factorized. An example of original RDF data is provided in *database/input* folder.
* path_to_output_RDF - Path to the folder to save the factorized RDF data. 

### Running An Example of SSN data

Example json file and original RDF data are provided in the *database* folder. Use the command below to run the example.

```
$java -jar target/RDFFactorization-0.0.1-SNAPSHOT.jar ./database/json-file/metadata.json ./database/input/  ./database//output/

```
