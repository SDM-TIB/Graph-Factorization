# Graph-Factorization
Graph Factorization project creates compact representations of RDF graphs by reducing the number of frequent star patterns (FSP) in the RDF graphs. In factorized representations of RDF graphs the number of RDF triples is reduced while preserving the knowledge encoded in the data. Graph factorization project requires a class and a set of corresponding properties, involved in frequent star patterns, to perform factorization. *EFSP* and *GFSP* perform FSP detection by identifying classes and properties involved in frequent star patterns. Running this project requires following steps:

1.  Configuration
2.  FSP Detection
3.  Factorization

# 1.  Configuration
In this step a docker image of ubuntu is created, and ubuntu image along with an other docker container running virtuoso endpoint are started using docker-compose.
```
$cd Graph-Factorization
$docker build -t ubuntu1804 .
$docker-compose up -d

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
