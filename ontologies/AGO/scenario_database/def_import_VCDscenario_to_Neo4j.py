import json
from vcd import core
from vcd.core import ElementType
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


class Neo4jScenarioDB:
    @staticmethod
    def clear_database():
        """
        Clear the database before reloading the ontology to delete the graph elements and removing existing constraints.
        """
        with session:
            # If reload=True --> first delete database elements:
            session.run(""" MATCH (n) DETACH DELETE n """)

    @staticmethod
    def add_property(labels, node_identifier, identifier_value, properties):
        cypher_labels = ''
        for label in labels:
            cypher_labels = cypher_labels + ':' + label
        for prop in properties:
            prop_type = type(properties[prop])
            with session:
                if prop_type == str:
                    session.run(""" MATCH (node:"""+cypher_labels+""") 
                                    WHERE node."""+node_identifier+"""='""" + identifier_value + """'
                                    SET node.""" + prop + """= '""" + properties[prop] + """' """)
                elif prop_type == list:
                    property_value = json.dumps(properties[prop])
                    session.run(""" MATCH (node:"""+cypher_labels+""") 
                                    WHERE node."""+node_identifier+"""='""" + identifier_value + """'
                                    SET node.""" + prop + """= '""" + property_value + """' """)

                elif prop_type == dict:
                    property_value = json.dumps(properties[prop])
                    session.run(""" MATCH (node:"""+cypher_labels+""") 
                                    WHERE node."""+node_identifier+"""='""" + identifier_value + """'
                                    SET node.""" + prop + """= '""" + property_value + """' """)

    @staticmethod
    def scenario_main_nodes(scenario_uid, cnl_text, schema_version):
        """
        :param main_label: Used to classify the nodes according to their source.
        :param scenario_id: The Scenarios will have a unique id.
        :param scenario_name: A friendly name defined as a label of the scenario (CamelCase).
        :param source: The source the scenario has been obtained from. For examples: dataset, recording, etc.
        :param cnl_text: The scenario description in text (CNL).
        :param keywords: A list (use ',' to separate them) of the main words.
        :return:
        """
        with session:
            session.run(""" MERGE (n:""" + scenario_uid + """:VCD:Scenario)
                            SET n.scenario_uid = '""" + scenario_uid + """',
                                n.cnl_text = '""" + cnl_text + """',
                                n.schema_version = '""" + schema_version + """' """)

            session.run(""" MATCH (n:""" + scenario_uid + """)
                            WHERE n.scenario_uid = '""" + scenario_uid + """'
                            MERGE (n)-[:has]->(m:""" + scenario_uid + """:Contexts) SET m.name = 'Contexts'
                            MERGE (n)-[:has]->(m1:""" + scenario_uid + """:Objects) SET m1.name = 'Objects'
                            MERGE (n)-[:has]->(m2:""" + scenario_uid + """:Actions) SET m2.name = 'Actions'
                            MERGE (n)-[:has]->(m3:""" + scenario_uid + """:Events) SET m3.name = 'Events' """)

    @staticmethod
    def create_scenario(scenario_uid: str, vcd: core.VCD = None, only_static=True):
        print("----------------------------------------")
        print("Adding {scenario_uid} scenario (only_static={only_static})".format(scenario_uid=scenario_uid,
                                                                                  only_static=only_static))
        print("----------------------------------------")
        with session:
            # Create base node
            # Read metadata from VCD
            main_node_properties = vcd.get_metadata()
            Neo4jScenarioDB.scenario_main_nodes(scenario_uid, main_node_properties['cnl_text'],
                                                main_node_properties['schema_version'])
            print("\tAdded main node({scenario_uid})".format(scenario_uid=scenario_uid))

            # Create streams / coordinate systems
            streams = vcd.get_streams()
            if len(streams) > 0:
                session.run(""" MATCH (n:""" + scenario_uid + """) WHERE n.scenario_uid = '""" + scenario_uid + """'
                                MERGE (n)-[:has]->(m:""" + scenario_uid + """:Streams) SET m.name = 'Streams' """)
                for stream_name, stream_content in vcd.get_streams().items():
                    session.run(""" MATCH (n:""" + scenario_uid + """:Streams) WHERE n.name = 'Streams'
                                    MERGE (n)-[:has]->(m:""" + scenario_uid + """:stream {name: '""" + stream_name + """'}) """)
                    Neo4jScenarioDB.add_property([scenario_uid, 'stream'], 'name', stream_name, stream_content)
            print("\tAdded {n} streams nodes".format(n=len(streams)))

            coordinate_systems = vcd.get_coordinate_systems()
            if len(coordinate_systems) > 0:
                session.run(""" MATCH (n:""" + scenario_uid + """) WHERE n.scenario_uid = '""" + scenario_uid + """'
                                MERGE (n)-[:has]->(m:""" + scenario_uid + """:Coordinate_systems) 
                                    SET m.name = 'Coordinate_systems' """)
                for cs_name, cs_content in vcd.get_coordinate_systems().items():
                    session.run(""" MATCH (n:""" + scenario_uid + """:Coordinate_systems) 
                                    WHERE n.name = 'Coordinate_systems'
                                    MERGE (n)-[:has]->(m:""" + scenario_uid + """:coordinate_system {name: '""" + cs_name + """'}) """)
                    Neo4jScenarioDB.add_property([scenario_uid, 'coordinate_system'], 'name', cs_name, cs_content)
            print("\tAdded {n} coordinate system nodes".format(n=len(streams)))

            # Create frames (with frame_properties, but without elements)
            if not only_static:
                # Frames node, then multiple frame nodes which contain
                fis_vcd = vcd.get_frame_intervals()
                if not fis_vcd.empty():
                    session.run(""" MATCH (n:""" + scenario_uid + """) WHERE n.scenario_uid = '""" + scenario_uid + """'
                                    MERGE (n)-[:has]->(m:""" + scenario_uid + """:Frames)
                                    SET m.name = 'Frames' """)

                    # Create frames
                    frame_count = 0
                    for fi in fis_vcd.get():
                        for frame_num in range(fi[0], fi[1] + 1):
                            # Add frame properties
                            frame = vcd.get_frame(frame_num)
                            if 'frame_properties' in frame:  # can contain "timestamp", "streams", "odometry", "transforms", etc
                                session.run(""" MATCH (n:""" + scenario_uid + """:Frames) WHERE n.name = 'Frames'
                                                MERGE (n)-[:has]->(m:""" + scenario_uid + """:frame) 
                                                SET m.frame='"""+frame_num+"""' """)
                            frame_count += 1
                print("\tAdded {} frames".format(frame_count))

            # Create elements (i.e. Objects, Actions, Contexts, Events)
            for element_type in ElementType:
                if element_type == ElementType.relation:  # Relations have special treatment
                    continue
                if vcd.has_elements(element_type):
                    # Create elements (e.g. objects)
                    element_uids = vcd.get_elements_uids(element_type=element_type)
                    for element_uid in element_uids:
                        # VCD element higher-level structure
                        element = vcd.get_element(element_type=element_type, uid=element_uid)
                        element_properties = {}
                        element_properties.update(uid=element_uid, name=element['name'], type=element['type'])
                        session.run(""" MATCH (n:""" + scenario_uid + """:"""+element_type.name.capitalize() + 's'+""") 
                                        WHERE n.name = '"""+element_type.name.capitalize() + 's'+"""'
                                        MERGE (n)-[:subClassOf]->(m:""" + scenario_uid + """:"""+element_type.name+""" {uid: '""" + element_uid + """'}) """)
                        Neo4jScenarioDB.add_property([scenario_uid, element_type.name], 'uid', element_uid, element_properties)

                        if 'ontology_uid' in element:
                            ontology_uid = element['ontology_uid']
                            session.run(""" MATCH (m:""" + scenario_uid + """:""" + element_type.name + """)
                                            WHERE m.name = '""" + element['name'] + """'
                                            SET m.ontology_uid = '""" + ontology_uid + """' """)
                        if 'frame_intervals' in element:
                            frame_intervals = json.dumps(element['frame_intervals'][0])
                            session.run(""" MATCH (m:""" + scenario_uid + """:""" + element_type.name + """)
                                            WHERE m.name = '""" + element['name'] + """'
                                            SET m.frame_intervals = '""" + frame_intervals + """' """)
                        if 'coordinate_system' in element:
                            coordinate_system = element['coordinate_system']
                            session.run(""" MATCH (m:""" + scenario_uid + """:""" + element_type.name + """)
                                            WHERE m.name = '""" + element['name'] + """'
                                            SET m.coordinate_system = '""" + coordinate_system + """' """)

                        # Create attributes
                        if only_static:
                            # Let's look only into static attributes
                            if element_type.name + '_data' in element:
                                ed_labels = [scenario_uid, element['name'], element_type.name + '_data']
                                element_data = element[element_type.name + '_data']
                                for ed_type in element_data:
                                    ed_array = element_data[ed_type]
                                    for ed in ed_array:
                                        ed_properties = ed
                                        ed_properties.update({'type': ed_type})
                                        for prop in ed_properties:
                                            if type(ed_properties[prop]) == str:
                                                session.run(""" MATCH (n:""" + scenario_uid + """:""" + element_type.name + """ {name:'"""+element['name']+"""'})
                                                                MERGE (n)-[:hasAttribute]->(m:"""+scenario_uid+""":"""+element['name']+""":"""+element_type.name + '_data'+""")
                                                                SET m.""" + prop + """= '""" + ed_properties[prop] + """' """)
                                            elif type(ed_properties[prop]) == list:
                                                property_value = json.dumps(ed_properties[prop])
                                                session.run(""" MATCH (n:""" + scenario_uid + """:""" + element_type.name + """ {name:'"""+element['name']+"""'})
                                                                MERGE (n)-[:hasAttribute]->(m:"""+scenario_uid+""":"""+element['name']+""":"""+element_type.name + '_data'+""")
                                                                SET m.""" + prop + """= '""" + property_value + """' """)
                            print("\t\tAdded all static attributes of {element_type} {uid}".format(
                                element_type=element_type.name, uid=element_uid))

                        else:
                            # Let's add all dynamic attributes (reading element_data_pointers for quick access)
                            if element_type.name + '_data_pointers' in element:
                                ed_labels = [scenario_uid, element['name'], element_type.name + '_data']
                                for edp_name in element[element_type.name + '_data_pointers']:
                                    edp_fis = element[element_type.name + '_data_pointers'][edp_name]['frame_intervals']
                                    edp_type = element[element_type.name + '_data_pointers'][edp_name]['type']

                                    if len(edp_fis) == 0:
                                        # Add frame properties
                                        ed_properties = vcd.get_element_data(element_type, element_uid, edp_name)
                                        ed_properties.update({'type': edp_type})

                                        for prop in ed_properties:
                                            if type(ed_properties[prop]) == str:
                                                session.run(""" MATCH (n:""" + scenario_uid + """:""" + element_type.name + """ {name:'"""+element['name']+"""'})
                                                                MERGE (n)-[:hasAttribute]->(m:"""+scenario_uid+""":"""+element['name']+""":"""+element_type.name + '_data'+""")
                                                                SET m.""" + prop + """= '""" + ed_properties[prop] + """' """)
                                            elif type(ed_properties[prop]) == list:
                                                property_value = json.dumps(ed_properties[prop])
                                                session.run(""" MATCH (n:""" + scenario_uid + """:""" + element_type.name + """ {name:'""" + element['name'] + """'})
                                                                MERGE (n)-[:hasAttribute]->(m:""" + scenario_uid + """:""" + element['name'] + """:""" + element_type.name + '_data' + """)
                                                                SET m.""" + prop + """= '""" + property_value + """' """)
                                    else:
                                        for fi in edp_fis:
                                            for frame_num in range(fi['frame_start'], fi['frame_end'] + 1):
                                                # Add frame properties
                                                ed_properties = vcd.get_element_data(element_type, element_uid, edp_name, frame_num)
                                                ed_properties.update({'frame': frame_num})
                                                ed_properties.update({'type': edp_type})

                                                for prop in ed_properties:
                                                    if type(ed_properties[prop]) == str:
                                                        session.run("""" MATCH (n:""" + scenario_uid + """:""" + element_type.name + """ {name:'""" + element['name'] + """'})
                                                                         MERGE (n)-[:hasAttribute]->(m:""" + scenario_uid + """:""" + element['name'] + """:""" + element_type.name + '_data' + """)
                                                                         SET m.""" + prop + """= '""" + ed_properties[prop] + """' """)
                                                    elif type(ed_properties[prop]) == list:
                                                        property_value = json.dumps(ed_properties[prop])
                                                        session.run("""" MATCH (n:""" + scenario_uid + """:""" + element_type.name + """ {name:'""" + element['name'] + """'})
                                                                         MERGE (n)-[:hasAttribute]->(m:""" + scenario_uid + """:""" + element['name'] + """:""" + element_type.name + '_data' + """)
                                                                         SET m.""" + prop + """= '""" + property_value + """' """)
                            print("\t\tAdded all dynamic attributes of {element_type} {uid}".format(
                                element_type=element_type.name, uid=element_uid))
                    print("\tAdded {n} {element} nodes".format(n=len(element_uids), element=element_type.name))

            # Special case Relations
            if vcd.has_relations():
                relations_uid = vcd.get_elements_uids(ElementType.relation)
                for relation_uid in relations_uid:
                    relation = vcd.get_relation(relation_uid)

                    rel_properties = {'name': relation['name'], 'uid': relation_uid}
                    if 'frame_intervals' in relation:
                        rel_properties.update({'frame_intervals': relation['frame_intervals']})

                    # Create neo4j relations between the involved elements (RDF subjects and objects)
                    relation_type = relation['type']  # e.g. "isPartOf"
                    relation_rdf_sub = relation['rdf_subjects']
                    relation_rdf_obj = relation['rdf_objects']
                    if len(relation_rdf_sub) > 0 and len(relation_rdf_obj) > 0:
                        # Let's read only the first rdf_subject and rdf-object for the moment
                        relation_rdf_sub_0 = relation_rdf_sub[0]
                        relation_rdf_obj_0 = relation_rdf_obj[0]

                        sub_uid = relation_rdf_sub_0['uid']
                        sub_type = relation_rdf_sub_0['type']
                        obj_uid = relation_rdf_obj_0['uid']
                        obj_type = relation_rdf_obj_0['type']

                        subject = vcd.get_element(element_type=ElementType[sub_type], uid=sub_uid)
                        object = vcd.get_element(element_type=ElementType[obj_type], uid=obj_uid)

                        session.run(""" MATCH (n:""" + scenario_uid + """ {name:'"""+subject['name']+"""'}), 
                                              (m:""" + scenario_uid + """ {name:'"""+object['name']+"""'})
                                        MERGE (n)-[r:"""+relation_type+"""]->(m)""")
            print("\tAdded {n} VCD relations".format(n=len(relations_uid)))
        session.close()
