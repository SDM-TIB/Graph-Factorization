# Graph-Factorization
Graph Factorization project creates compact representations of RDF graphs by reducing the number of frequent star patterns in the RDF graphs. In factorized representations of RDF graphs number of RDF triples is reduced while preserving the knowledge encoded in the data. 

## Create Maven Package

```
$mvn package

```

## Run Factorization

```
$java -jar target/RDFFactorization-0.0.1-SNAPSHOT.jar path_to_json_file path_to_input_folder_original_RDF path_to_output_folder_factorized_RDF
```
### Parameters
*path_to_json_file - Path to json file containing a class and corresponding properties to perform factorization. An example of json file is provided in "database/json-file" folder.
*path_to_input_folder_original_RDF - Path to the folder conataining original RDF to be factorized. An example of original RDF data is provided in "database/input" folder.
*path_to_output_folder_factorized_RDF - Path to the folder to save the factorized RDF data. 

### Running An Example of SSN data
An example of json file, original RDF data folder and a fodler to save the factorized RDF data is provided in *database* folder. Use the command below to run the example.

```
$java -jar target/RDFFactorization-0.0.1-SNAPSHOT.jar ./database/json-file/metadata.json ./database/input/  ./database//output/

```
