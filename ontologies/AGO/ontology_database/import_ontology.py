# Import ontology to Neo4j to construct AGO:
from def_ontology_import import Neo4jOntologyDB
# Input parameters:
# Full path of the ontology file:
owl_file = '../AGO/ontology_database/OWL/AGO1.0.0.owl'

serialization_format = 'RDF/XML'  # Valid formats: Turtle, N-Triples, JSON-LD, TriG, RDF/XML
ontology_label = 'AGO'
Reload_ontology = True  # Select 'False' if it is the first time loading the ontology.
                        # Select 'True' to delete tha database content before loading the ontology.
# Metadata
version = "1.0.0"
title = "Automotive Global Ontology"
language = "en"
creator = "Itziar Urbieta"
publisher = "Vicomtech"
description = "This is a global ontology of the main concepts related with the automotive area. The " \
              "ontology contains the constructs required for annotation and traffic scenario simulation."

# Import the elements of the ontology file
Neo4jOntologyDB.import_taxonomy(owl_file, Reload_ontology, ontology_label, serialization_format, version, title,
                                language, creator, publisher, description)





