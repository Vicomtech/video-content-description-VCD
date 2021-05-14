# Automotive Global Ontology (AGO)

AGO is an automotive domain ontology built based on the structure of graphs. The concepts to build the knowledge-base have been obtained from diverse, heterogeneous data sources and taxonomies (e.g. from large existing Advanced Driver Assistance Systems (ADAS) and Autonomous Driving (AD) open datasets). 

The ontology has been built to support semantic labeling and the description of automotive scenarios for testing in simulation environments. To this end, higher-level semantic relationships have been included in the knowledge-base providing meaning to the labels and scenario descriptions. Thus, the format of data is detached from meaning, and standard practices can be safely used, such as the Video Content Description ([VCD](http://vcd.vicomtech.org)) language or the upcoming [ASAM OpenLabel](https://www.asam.net/active-projects/) standard. The VCD structure permits labeling an entire scene in a single file including actions, attributes and relations in the form of RDF triples which makes it ideal for the use considered use cases.

The files published in this repository reflect the first steps towards the established objectives. In this way, here you will find files with the following characteristics:
* AGO ontology in OWL format.
* Importing file to create an ontology graph in [Neo4j](https://neo4j.com/download-neo4j-now/?utm_program=emea-prospecting&utm_source=google&utm_medium=cpc&utm_campaign=emea-search-branded&utm_adgroup=neo4j-desktop&gclid=CjwKCAjwnPOEBhA0EiwA609ReUjV7vE8SzR0JeEoH7kE5i73QM7X_tiLlFC-YAOoSJKpmUUbsuixOhoCdssQAvD_BwE).
* Examples of functional scenarios in VCD format for:
    * The [KITTI dataset](http://www.cvlibs.net/datasets/kitti/eval\_tracking.php).
    * The critical scenarios defined in the [ALKS regulation](https://undocs.org/ECE/TRANS/WP.29/2020/81).
* Importing file to include VCD scenarios into Neo4j.


## A) Ontology graph construction
### Requirements
* Install Neo4j graph database. 
* Install the [neosemantics (n10s)](https://github.com/neo4j-labs/neosemantics) plugin.

### Basic flow
The ontology file is an OWL file written in RDF/XML syntax and defined in Protégé. The file can be found at:
````
/ontologies/AGO/ontology_database/OWL/AGO1.0.0.owl
````

The first step is to set the Neo4j authentification parameter as defined in **neo4j.json** located in:
````
/ontologies/AGO/etc/neo4j.json
````

The script **import_ontology.py** has been defined in order to construct the AGO graph in Neo4j. The main script can be found at:
````
/ontologies/AGO/ontology_database/import_ontology.py
````

Before running the script first Neo4j must be running. In addition, several parameters should be configured in the main file:
* Set the full path of the ontology file (For example the 'url': ````http://vcd.vicomtech.org/ontology/automotive````).
* If it is the first time loading the ontology in the Neo4j database set:
```python
Reload_ontology = True
```



## B) Scenario database generation
### Requirements
* Install Neo4j.
* Install 'vcd' python package.
* Prepare VCD scenario files.

### Basic flow
The VCD functional scenario files are divided in two folders according to the data-source:
````
/ontologies/AGO/scenario_database/VCD_files/ALKS/*.json
/ontologies/AGO/scenario_database/VCD_files/KITTI/*.json
````

First, set the Neo4j authentification parameter as defined in **neo4j.json** located in:
````
/ontologies/AGO/etc/neo4j.json
````

The main file **import_scenario.py** is configured to load all the files. In order to execute the script, Neo4j must be running. Download the VCD files and set the path before running the script. 
