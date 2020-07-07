# Neo4j driver session
from neo4j.v1 import GraphDatabase, basic_auth
driver = GraphDatabase.driver("bolt://galtzagorri:7658", auth=basic_auth(user = "neo4j", password = "galtzagorri"), encrypted=False) 

session = driver.session()

with session:
	session.run("""CREATE INDEX ON :Resource(uri)""")
	session.run("""CALL semantics.importRDF("file:/media/data/home_folders/VICOMTECH/iurbieta/neo4j-community-3.5.12/import/GlobalOntology1.2.0.rdf","RDF/XML", { handleVocabUris: "IGNORE" }) """)