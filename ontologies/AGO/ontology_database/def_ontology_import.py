import json
from neo4j import GraphDatabase, basic_auth

with open("../etc/neo4j.json") as config_file:
    config = json.load(config_file)
    host = config['host']
    port = config['port']
    user = config['user']
    password = config['password']

# Connection with Neo4j:
driver = GraphDatabase.driver('bolt://'+host+":"+port, auth=basic_auth(user=user, password=password), encrypted=False)
session = driver.session()


class Neo4jOntologyDB:
    @staticmethod
    def clear_database():
        """
        Clear the database before reloading the ontology to delete the graph elements and removing existing constraints.
        """
        with session:
            # If reload=True --> first delete database elements:
            session.run(""" MATCH (n) DETACH DELETE n """)
            session.run(""" DROP CONSTRAINT ON (n:Resource) ASSERT n.uri IS UNIQUE """)

    @staticmethod
    def add_neo4j_labels(label):
        """
        Classify Neo4j nodes according to the core-elements by including neo4j-labels.
        """
        # Add the general label 'Class' for every element of the taxonomy:
        session.run(""" MATCH (n:""" + label + """) SET n:Class """)

        # Include Neo4j-labels to classify the Classes:
        for term in ['Object', 'Action', 'Context', 'Event']:
            session.run(""" MATCH (start:""" + label + """:Class) WHERE start.label='""" + term + """'
                            MATCH p=(start)<-[*]-(end:Class:""" + label + """)
                            WHERE not (end)<--(:Class:""" + label + """)
                            UNWIND nodes(p) as pathNodes
                            SET pathNodes:""" + term + """ """)

    @staticmethod
    def add_metadata(version: str, title: str, language: str, creator: str, publisher: str, label: str,
                     description: str):
        """
        This functions adds metadata to the ontology
        """
        with session:
            session.run(""" MERGE (n:Ontology:metadata)
                            SET n.version='""" + version + """', 
                                n.title='""" + title + """', 
                                n.language='""" + language + """',
                                n.creator='""" + creator + """',
                                n.publisher='""" + publisher + """',
                                n.label='""" + label + """', 
                                n.description='""" + description + """' """)

    @staticmethod
    def import_taxonomy(owl_file, Reload, ontology_label, serialization_format, version, title, language, creator, publisher,
                        description):
        """
        Import the ontology into the Neo4j database using neosemantics (n10s) plugin.
        """
        if Reload is True:
            Neo4jOntologyDB.clear_database()
            # Create Index:
            session.run(""" CREATE CONSTRAINT n10s_unique_uri ON (r:Resource)
                                                    ASSERT r.uri IS UNIQUE; """)
            session.run(""" CALL n10s.graphconfig.init(); """)
        else:
            pass
        # Load data
        if 'http' in owl_file:
            session.run(""" CALL n10s.onto.import.fetch('""" + owl_file + """', '""" + serialization_format + """', 
                                                        {classLabel: '""" + ontology_label + """',
                                                        subClassOfRel: 'subClassOf',
                                                        dataTypePropertyLabel: 'dataProperty',
                                                        objectPropertyLabel: 'objectProperty',
                                                        subPropertyOfRel: 'subPropertyOf'}) """)
        else:
            session.run(""" CALL n10s.onto.import.fetch('file:///"""+owl_file+"""', '"""+serialization_format+"""', 
                                            {classLabel: '"""+ontology_label+"""',
                                            subClassOfRel: 'subClassOf',
                                            dataTypePropertyLabel: 'dataProperty',
                                            objectPropertyLabel: 'objectProperty',
                                            subPropertyOfRel: 'subPropertyOf'}) """)
        Neo4jOntologyDB.add_neo4j_labels(ontology_label)
        Neo4jOntologyDB.add_metadata(version, title, language, creator, publisher, ontology_label, description)
        session.close()
        print("Loaded ontology from: {owl_file}".format(owl_file=owl_file))