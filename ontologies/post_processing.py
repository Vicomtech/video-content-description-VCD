# Post processing stage:

# Neo4j driver session
from neo4j.v1 import GraphDatabase, basic_auth
driver = GraphDatabase.driver("bolt://galtzagorri:7658", auth=basic_auth(user = "neo4j", password = "galtzagorri"), encrypted=False) 

session = driver.session()

with session:

	session.run(""" MATCH (n:Resource)
					SET n:`GlobalOntology1.2.0` """)
	session.run(""" MATCH (n:`GlobalOntology1.2.0`)<-[*]-(m), (t:`GlobalOntology1.2.0`)<-[*]-(u)  
					WHERE n.label='Action' and t.label='Attribute'
					SET m:Action
					SET u:Attribute """)
	session.run(""" MATCH (n:`GlobalOntology1.2.0`:Class) 
					WHERE not n:Action and not n:Attribute
					SET n:Object """)
	session.run(""" MATCH (n) REMOVE n:Resource """)
	session.run(""" DROP INDEX ON :Resource(uri) """)
	session.run(""" //Pedestrian transitive
					MATCH (ped:`GlobalOntology1.2.0`) WHERE ped.label='Pedestrian'
					MATCH (q:`GlobalOntology1.2.0`) WHERE q.label='Walking along'
					MATCH (q1:`GlobalOntology1.2.0`) WHERE q1.label='Crossing'
					MATCH (q2:`GlobalOntology1.2.0`) WHERE q2.label='Following'
					MATCH (q3:`GlobalOntology1.2.0`) WHERE q3.label='Approaching'
					MATCH (q4:`GlobalOntology1.2.0`) WHERE q4.label='Sitting on'
					MATCH (q5:`GlobalOntology1.2.0`) WHERE q5.label='Standing on'
					MATCH (w:`GlobalOntology1.2.0`) WHERE w.label='Footwalk'
					MATCH (w1:`GlobalOntology1.2.0`) WHERE w1.label='Parking'
					MATCH (w2:`GlobalOntology1.2.0`) WHERE w2.label='Pedestrian area'
					MATCH (w3:`GlobalOntology1.2.0`) WHERE w3.label='Sidewalk'
					MATCH (e:`GlobalOntology1.2.0`) WHERE e.label='Crosswalk'
					MATCH (e1:`GlobalOntology1.2.0`) WHERE e1.label='Road'
					MATCH (e2:`GlobalOntology1.2.0`) WHERE e2.label='Bridge'
					MATCH (e3:`GlobalOntology1.2.0`) WHERE e3.label='Tunnel'
					MATCH (e4:`GlobalOntology1.2.0`) WHERE e4.label='Bike lane'
					MATCH (e5:`GlobalOntology1.2.0`) WHERE e5.label='Pedestrian area'
					MATCH (e6:`GlobalOntology1.2.0`) WHERE e6.label='Fence'
					MATCH (t:`GlobalOntology1.2.0`) WHERE t.label='Pedestrian'
					MATCH (t1:`GlobalOntology1.2.0`) WHERE t1.label='Animal'
					MATCH (y:`GlobalOntology1.2.0`) WHERE y.label='Intersection'
					MATCH (y1:`GlobalOntology1.2.0`) WHERE y1.label='Crosswalk'
					MATCH (y2:`GlobalOntology1.2.0`) WHERE y2.label='Object'
					MATCH (s:`GlobalOntology1.2.0`) WHERE s.label='Cycle'
					MATCH (s1:`GlobalOntology1.2.0`) WHERE s1.label='Terrain'
					MATCH (s2:`GlobalOntology1.2.0`) WHERE s2.label='Fence'
					MATCH (s3:`GlobalOntology1.2.0`) WHERE s3.label='Pole'
					MATCH (s4:`GlobalOntology1.2.0`) WHERE s4.label='Bike rack'
					MATCH (s5:`GlobalOntology1.2.0`) WHERE s5.label='Guard rail'
					MATCH (s6:`GlobalOntology1.2.0`) WHERE s6.label='Stroller'
					MATCH (s7:`GlobalOntology1.2.0`) WHERE s7.label='Wheelchair'
					MATCH (s8:`GlobalOntology1.2.0`) WHERE s8.label='Bridge'
					MATCH (s9:`GlobalOntology1.2.0`) WHERE s9.label='Bench'
					MATCH (s10:`GlobalOntology1.2.0`) WHERE s10.label='Personal mobility'
					MATCH (s11:`GlobalOntology1.2.0`) WHERE s11.label='Roadside object'
					MATCH (s12:`GlobalOntology1.2.0`) WHERE s12.label='Road'
					MATCH (s13:`GlobalOntology1.2.0`) WHERE s13.label='Crosswalk'
					MATCH (s14:`GlobalOntology1.2.0`) WHERE s14.label='Sidewalk'
					MATCH (s15:`GlobalOntology1.2.0`) WHERE s15.label='Footwalk'
					MATCH (s16:`GlobalOntology1.2.0`) WHERE s16.label='Bump'
					MATCH (s17:`GlobalOntology1.2.0`) WHERE s17.label='Curb'
					MERGE (ped)-[:isSubjectOfAction]->(q)
					MERGE (w)-[:isObjectOfAction]->(q)
					MERGE (w1)-[:isObjectOfAction]->(q)
					MERGE (w2)-[:isObjectOfAction]->(q)
					MERGE (w3)-[:isObjectOfAction]->(q)
					MERGE (ped)-[:isSubjectOfAction]->(q1)
					MERGE (e)-[:isObjectOfAction]->(q1)
					MERGE (e1)-[:isObjectOfAction]->(q1)
					MERGE (e2)-[:isObjectOfAction]->(q1)
					MERGE (e3)-[:isObjectOfAction]->(q1)
					MERGE (e4)-[:isObjectOfAction]->(q1)
					MERGE (e5)-[:isObjectOfAction]->(q1)
					MERGE (e6)-[:isObjectOfAction]->(q1)
					MERGE (ped)-[:isSubjectOfAction]->(q2)
					MERGE (t)-[:isObjectOfAction]->(q2)
					MERGE (t1)-[:isObjectOfAction]->(q2)
					MERGE (ped)-[:isSubjectOfAction]->(q3)
					MERGE (y)-[:isObjectOfAction]->(q3)
					MERGE (y1)-[:isObjectOfAction]->(q3)
					MERGE (y2)-[:isObjectOfAction]->(q3)
					MERGE (ped)-[:isSubjectOfAction]->(q4)
					MERGE (q4)<-[:isObjectOfAction]-(s)
					MERGE (q4)<-[:isObjectOfAction]-(s1)
					MERGE (q4)<-[:isObjectOfAction]-(s2)
					MERGE (q4)<-[:isObjectOfAction]-(s3)
					MERGE (q4)<-[:isObjectOfAction]-(s4)
					MERGE (q4)<-[:isObjectOfAction]-(s5)
					MERGE (q4)<-[:isObjectOfAction]-(s6)
					MERGE (q4)<-[:isObjectOfAction]-(s7)
					MERGE (q4)<-[:isObjectOfAction]-(s8)
					MERGE (q4)<-[:isObjectOfAction]-(s9)
					MERGE (q4)<-[:isObjectOfAction]-(s10)
					MERGE (q4)<-[:isObjectOfAction]-(s11)
					MERGE (ped)-[:isSubjectOfAction]-(q5)
					MERGE (q5)<-[:isObjectOfAction]-(s1)
					MERGE (q5)<-[:isObjectOfAction]-(s6)
					MERGE (q5)<-[:isObjectOfAction]-(s8)
					MERGE (q5)<-[:isObjectOfAction]-(s9)
					MERGE (q5)<-[:isObjectOfAction]-(s11)
					MERGE (q5)<-[:isObjectOfAction]-(s12)
					MERGE (q5)<-[:isObjectOfAction]-(s13)
					MERGE (q5)<-[:isObjectOfAction]-(s14)
					MERGE (q5)<-[:isObjectOfAction]-(s15)
					MERGE (q5)<-[:isObjectOfAction]-(s16)
					MERGE (q5)<-[:isObjectOfAction]-(s17) """)
	session.run (""" //Pedestrian intransitive
					MATCH (ped:`GlobalOntology1.2.0`) WHERE ped.label='Pedestrian'
					MATCH (n:`GlobalOntology1.2.0`) WHERE n.label='Sitting'
					MATCH (n1:`GlobalOntology1.2.0`) WHERE n1.label='Standing'
					MATCH (m:`GlobalOntology1.2.0`) WHERE m.label='Traffic violation'
					MATCH (m1:`GlobalOntology1.2.0`) WHERE m1.label='Running'
					MATCH (m2:`GlobalOntology1.2.0`) WHERE m2.label='Gliding on wheels'
					MATCH (m3:`GlobalOntology1.2.0`) WHERE m3.label='Standstill'
					MATCH (m4:`GlobalOntology1.2.0`) WHERE m4.label='Waiting'
					MATCH (m5:`GlobalOntology1.2.0`) WHERE m5.label='Moving straight'
					MATCH (m6:`GlobalOntology1.2.0`) WHERE m6.label='Unclassified'
					MATCH (m7:`GlobalOntology1.2.0`) WHERE m7.label='Walking'
					MERGE (ped)-[:performsAction]->(n)
					MERGE (ped)-[:performsAction]->(n1)
					MERGE (ped)-[:performsAction]->(m)
					MERGE (ped)-[:performsAction]->(m1)
					MERGE (ped)-[:performsAction]->(m2)
					MERGE (ped)-[:performsAction]->(m3)
					MERGE (ped)-[:performsAction]->(m4)
					MERGE (ped)-[:performsAction]->(m5)
					MERGE (ped)-[:performsAction]->(m6)
					MERGE (ped)-[:performsAction]->(m7)	 """)
	session.run(""" //Veh transitive
					MATCH (veh:`GlobalOntology1.2.0`) WHERE veh.label='Road vehicle'
					MATCH (q1:`GlobalOntology1.2.0`) WHERE q1.label='Crossing'
					MATCH (q2:`GlobalOntology1.2.0`) WHERE q2.label='Following'
					MATCH (q3:`GlobalOntology1.2.0`) WHERE q3.label='Approaching'
					MATCH (q4:`GlobalOntology1.2.0`) WHERE q4.label='Fall behind'
					MATCH (q5:`GlobalOntology1.2.0`) WHERE q5.label='Passing'
					MATCH (q6:`GlobalOntology1.2.0`) WHERE q6.label='Turning into left'
					MATCH (q7:`GlobalOntology1.2.0`) WHERE q7.label='Turning into right'
					MATCH (q8:`GlobalOntology1.2.0`) WHERE q8.label='Lane changing into left'
					MATCH (q9:`GlobalOntology1.2.0`) WHERE q9.label='Lane changing into right'
					MATCH (q10:`GlobalOntology1.2.0`) WHERE q10.label='Stopped in'
					MATCH (q11:`GlobalOntology1.2.0`) WHERE q11.label='Parked in'
					MATCH (w:`GlobalOntology1.2.0`) WHERE w.label='Intersection'
					MATCH (w1:`GlobalOntology1.2.0`) WHERE w1.label='Road'
					MATCH (e:`GlobalOntology1.2.0`) WHERE e.label='Road vehicle'
					MATCH (e1:`GlobalOntology1.2.0`) WHERE e1.label='Rider'
					MATCH (y:`GlobalOntology1.2.0`) WHERE y.label='Intersection'
					MATCH (y1:`GlobalOntology1.2.0`) WHERE y1.label='Crosswalk'
					MATCH (y2:`GlobalOntology1.2.0`) WHERE y2.label='Object'
					MATCH (l:`GlobalOntology1.2.0`) WHERE l.label='Lane'
					MATCH (l1:`GlobalOntology1.2.0`) WHERE l1.label='Parking'
					MATCH (l2:`GlobalOntology1.2.0`) WHERE l2.label='Service lane'
					MATCH (l3:`GlobalOntology1.2.0`) WHERE l3.label='Bike lane'
					MATCH (l4:`GlobalOntology1.2.0`) WHERE l4.label='Footwalk'
					MATCH (l5:`GlobalOntology1.2.0`) WHERE l5.label='Sidewalk'
					MERGE (veh)-[:isSubjectOfAction]->(q1)
					MERGE (w)-[:isObjectOfAction]->(q1)
					MERGE (w1)-[:isObjectOfAction]->(q1)
					MERGE (e)-[:isObjectOfAction]->(q2)
					MERGE (e1)-[:isObjectOfAction]->(q2)
					MERGE (veh)-[:isSubjectOfAction]->(q3)
					MERGE (y)-[:isObjectOfAction]->(q3)
					MERGE (y1)-[:isObjectOfAction]->(q3)
					MERGE (y2)-[:isObjectOfAction]->(q3)
					MERGE (veh)-[:isSubjectOfAction]->(q4)
					MERGE (e)-[:isObjectOfAction]->(q4)
					MERGE (e1)-[:isObjectOfAction]->(q4)
					MERGE (veh)-[:isSubjectOfAction]->(q5)
					MERGE (e)-[:isObjectOfAction]->(q5)
					MERGE (e1)-[:isObjectOfAction]->(q5)
					MERGE (veh)-[:isSubjectOfAction]->(q6)
					MERGE (w)-[:isObjectOfAction]->(q6)
					MERGE (w1)-[:isObjectOfAction]->(q6)
					MERGE (l)-[:isObjectOfAction]->(q6)
					MERGE (l1)-[:isObjectOfAction]->(q6)
					MERGE (l2)-[:isObjectOfAction]->(q6)
					MERGE (l3)-[:isObjectOfAction]->(q6)
					MERGE (l4)-[:isObjectOfAction]->(q6)
					MERGE (l5)-[:isObjectOfAction]->(q6)
					MERGE (veh)-[:isSubjectOfAction]->(q7)
					MERGE (w)-[:isObjectOfAction]->(q7)
					MERGE (w1)-[:isObjectOfAction]->(q7)
					MERGE (l)-[:isObjectOfAction]->(q7)
					MERGE (l1)-[:isObjectOfAction]->(q7)
					MERGE (l2)-[:isObjectOfAction]->(q7)
					MERGE (l3)-[:isObjectOfAction]->(q7)
					MERGE (l4)-[:isObjectOfAction]->(q7)
					MERGE (l5)-[:isObjectOfAction]->(q7)
					MERGE (veh)-[:isSubjectOfAction]->(q8)
					MERGE (l)-[:isObjectOfAction]->(q8)
					MERGE (veh)-[:isSubjectOfAction]->(q9)
					MERGE (l)-[:isObjectOfAction]->(q9)
					MERGE (veh)-[:isSubjectOfAction]->(q10)
					MERGE (l5)-[:isObjectOfAction]->(q10)
					MERGE (l)-[:isObjectOfAction]->(q10)
					MERGE (w1)-[:isObjectOfAction]->(q10)
					MERGE (l1)-[:isObjectOfAction]->(q10)
					MERGE (l2)-[:isObjectOfAction]->(q10)
					MERGE (veh)-[:isSubjectOfAction]->(q11)
					MERGE (l5)-[:isObjectOfAction]->(q11)
					MERGE (l)-[:isObjectOfAction]->(q11)
					MERGE (w1)-[:isObjectOfAction]->(q11)
					MERGE (l1)-[:isObjectOfAction]->(q11)
					MERGE (l2)-[:isObjectOfAction]->(q11) """)
	session.run(""" //Veh intransitive
					MATCH (veh:`GlobalOntology1.2.0`) WHERE veh.label='Road vehicle'
					MATCH (n:`GlobalOntology1.2.0`) WHERE n.label='Parked'
					MATCH (n1:`GlobalOntology1.2.0`) WHERE n1.label='Stopped'
					MATCH (m:`GlobalOntology1.2.0`) WHERE m.label='Traffic violation'
					MATCH (m1:`GlobalOntology1.2.0`) WHERE m1.label='Driving straight'
					MATCH (m2:`GlobalOntology1.2.0`) WHERE m2.label='Gliding on wheels'
					MATCH (m3:`GlobalOntology1.2.0`) WHERE m3.label='Lane changing right'
					MATCH (m4:`GlobalOntology1.2.0`) WHERE m4.label='Lane changing left'
					MATCH (m5:`GlobalOntology1.2.0`) WHERE m5.label='Turning right'
					MATCH (m6:`GlobalOntology1.2.0`) WHERE m6.label='Turning left'
					MATCH (m7:`GlobalOntology1.2.0`) WHERE m7.label='Loss of control'
					MATCH (m9:`GlobalOntology1.2.0`) WHERE m9.label='Reversing'
					MATCH (m10:`GlobalOntology1.2.0`) WHERE m10.label='uTurn'
					MATCH (m8:`GlobalOntology1.2.0`) WHERE m8.label='Unclassified'
					MATCH (m11:`GlobalOntology1.2.0`) WHERE m11.label='Driveaway'
					MATCH (m12:`GlobalOntology1.2.0`) WHERE m12.label='Halt'
					MATCH (m13:`GlobalOntology1.2.0`) WHERE m13.label='Parking'
					MATCH (m14:`GlobalOntology1.2.0`) WHERE m14.label='Safe stop'
					MATCH (m15:`GlobalOntology1.2.0`) WHERE m15.label='Waiting'
					MERGE (veh)-[:performsAction]->(m8)
					MERGE (veh)-[:performsAction]->(n)
					MERGE (veh)-[:performsAction]->(n1)
					MERGE (veh)-[:performsAction]->(m)
					MERGE (veh)-[:performsAction]->(m1)
					MERGE (veh)-[:performsAction]->(m2)
					MERGE (veh)-[:performsAction]->(m3)
					MERGE (veh)-[:performsAction]->(m4)
					MERGE (veh)-[:performsAction]->(m5)
					MERGE (veh)-[:performsAction]->(m6)
					MERGE (veh)-[:performsAction]->(m7)
					MERGE (veh)-[:performsAction]->(m9)
					MERGE (veh)-[:performsAction]->(m10)
					MERGE (veh)-[:performsAction]->(m11)
					MERGE (veh)-[:performsAction]->(m12)
					MERGE (veh)-[:performsAction]->(m13)
					MERGE (veh)-[:performsAction]->(m14)
					MERGE (veh)-[:performsAction]->(m15) """)
					
	session.run(""" //Animal transitive
					MATCH (anim:`GlobalOntology1.2.0`) WHERE anim.label='Animal'
					MATCH (q:`GlobalOntology1.2.0`) WHERE q.label='Walking along'
					MATCH (q1:`GlobalOntology1.2.0`) WHERE q1.label='Crossing'
					MATCH (q2:`GlobalOntology1.2.0`) WHERE q2.label='Following'
					MATCH (q3:`GlobalOntology1.2.0`) WHERE q3.label='Approaching'
					MATCH (q4:`GlobalOntology1.2.0`) WHERE q4.label='Sitting on'
					MATCH (w:`GlobalOntology1.2.0`) WHERE w.label='Footwalk'
					MATCH (w1:`GlobalOntology1.2.0`) WHERE w1.label='Parking'
					MATCH (w2:`GlobalOntology1.2.0`) WHERE w2.label='Pedestrian area'
					MATCH (w3:`GlobalOntology1.2.0`) WHERE w3.label='Sidewalk'
					MATCH (e:`GlobalOntology1.2.0`) WHERE e.label='Crosswalk'
					MATCH (e1:`GlobalOntology1.2.0`) WHERE e1.label='Road'
					MATCH (e2:`GlobalOntology1.2.0`) WHERE e2.label='Bridge'
					MATCH (e3:`GlobalOntology1.2.0`) WHERE e3.label='Tunnel'
					MATCH (e4:`GlobalOntology1.2.0`) WHERE e4.label='Bike lane'
					MATCH (e5:`GlobalOntology1.2.0`) WHERE e5.label='Pedestrian area'
					MATCH (e6:`GlobalOntology1.2.0`) WHERE e6.label='Fence'
					MATCH (t:`GlobalOntology1.2.0`) WHERE t.label='Pedestrian'
					MATCH (t1:`GlobalOntology1.2.0`) WHERE t1.label='Animal'
					MATCH (y:`GlobalOntology1.2.0`) WHERE y.label='Intersection'
					MATCH (y1:`GlobalOntology1.2.0`) WHERE y1.label='Crosswalk'
					MATCH (y2:`GlobalOntology1.2.0`) WHERE y2.label='Object'
					MATCH (p:`GlobalOntology1.2.0`) WHERE p.label='Bench'
					MERGE (anim)-[:isSubjectOfAction]->(q)
					MERGE (w)-[:isObjectOfAction]->(q)
					MERGE (w1)-[:isObjectOfAction]->(q)
					MERGE (w2)-[:isObjectOfAction]->(q)
					MERGE (w3)-[:isObjectOfAction]->(q)
					MERGE (anim)-[:isSubjectOfAction]->(q1)
					MERGE (e)-[:isObjectOfAction]->(q1)
					MERGE (e1)-[:isObjectOfAction]->(q1)
					MERGE (e2)-[:isObjectOfAction]->(q1)
					MERGE (e3)-[:isObjectOfAction]->(q1)
					MERGE (e4)-[:isObjectOfAction]->(q1)
					MERGE (e5)-[:isObjectOfAction]->(q1)
					MERGE (e6)-[:isObjectOfAction]->(q1)
					MERGE (anim)-[:isSubjectOfAction]->(q2)
					MERGE (t)-[:isObjectOfAction]->(q2)
					MERGE (t1)-[:isObjectOfAction]->(q2)
					MERGE (anim)-[:isSubjectOfAction]->(q3)
					MERGE (y)-[:isObjectOfAction]->(q3)
					MERGE (y1)-[:isObjectOfAction]->(q3)
					MERGE (y2)-[:isObjectOfAction]->(q3)
					MERGE (anim)-[:isSubjectOfAction]->(q4)
					MERGE (e1)-[:isObjectOfAction]->(q4)
					MERGE (p)-[:isObjectOfAction]->(q4)
					MERGE (e)-[:isObjectOfAction]->(q4)
					MERGE (w)-[:isObjectOfAction]->(q4)
					MERGE (e4)-[:isObjectOfAction]->(q4) """)				
	session.run(""" //Animal intransitive
					MATCH (anim:`GlobalOntology1.2.0`) WHERE anim.label='Animal'
					MATCH (n:`GlobalOntology1.2.0`) WHERE n.label='Sitting'
					MATCH (m:`GlobalOntology1.2.0`) WHERE m.label='Standing'
					MATCH (m10:`GlobalOntology1.2.0`) WHERE m10.label='Running'
					MATCH (m8:`GlobalOntology1.2.0`) WHERE m8.label='Unclassified'
					MATCH (m4:`GlobalOntology1.2.0`) WHERE m4.label='Waiting'
					MATCH (m5:`GlobalOntology1.2.0`) WHERE m5.label='Moving straight'
					MATCH (m6:`GlobalOntology1.2.0`) WHERE m6.label='Walking'
					MERGE (anim)-[:performsAction]->(n)
					MERGE (anim)-[:performsAction]->(m)
					MERGE (anim)-[:performsAction]->(m10)
					MERGE (anim)-[:performsAction]->(m8)
					MERGE (anim)-[:performsAction]->(m4)
					MERGE (anim)-[:performsAction]->(m5)
					MERGE (anim)-[:performsAction]->(m6) """)
	session.run(""" //Human
					MATCH (n:`GlobalOntology1.2.0`) WHERE n.label='Human'
					MATCH (q:`GlobalOntology1.2.0`) WHERE q.label='Age' 
					MATCH (q1:`GlobalOntology1.2.0`) WHERE q1.label='Gender'
					MATCH (q2:`GlobalOntology1.2.0`) WHERE q2.label='Nationality' 
					MATCH (q3:`GlobalOntology1.2.0`) WHERE q3.label='Height' 
					MATCH (q4:`GlobalOntology1.2.0`) WHERE q4.label='Hair' 
					MATCH (q5:`GlobalOntology1.2.0`) WHERE q5.label='Skin color' 
					MATCH (q6:`GlobalOntology1.2.0`) WHERE q6.label='Clothes' 
					MATCH (q7:`GlobalOntology1.2.0`) WHERE q7.label='Accessories' 
					MATCH (q8:`GlobalOntology1.2.0`) WHERE q8.label='Carrying object' 
					MERGE (n)-[:hasAttribute]->(q)
					MERGE (n)-[:hasAttribute]->(q1)
					MERGE (n)-[:hasAttribute]->(q2)
					MERGE (n)-[:hasAttribute]->(q3)
					MERGE (n)-[:hasAttribute]->(q4)
					MERGE (n)-[:hasAttribute]->(q5)
					MERGE (n)-[:hasAttribute]->(q6)
					MERGE (n)-[:hasAttribute]->(q7)
					MERGE (n)-[:hasAttribute]->(q8) """)		
	session.run(""" //Vehicle
					MATCH (n:`GlobalOntology1.2.0`) WHERE n.label='Road vehicle'
					MATCH (q:`GlobalOntology1.2.0`) WHERE q.label='Speed' 
					MATCH (q1:`GlobalOntology1.2.0`) WHERE q1.label='Manufacturer'//Brand 
					MATCH (q2:`GlobalOntology1.2.0`) WHERE q2.label='Color' 
					MATCH (q3:`GlobalOntology1.2.0`) WHERE q3.label='Model' 
					MATCH (q4:`GlobalOntology1.2.0`) WHERE q4.label='Fuel type' 
					MATCH (q5:`GlobalOntology1.2.0`) WHERE q5.label='Capacity' 
					MATCH (q6:`GlobalOntology1.2.0`) WHERE q6.label='Doors' 
					MATCH (q7:`GlobalOntology1.2.0`) WHERE q7.label='Connectivity' 
					MATCH (q8:`GlobalOntology1.2.0`) WHERE q8.label='Media'
					MATCH (q9:`GlobalOntology1.2.0`) WHERE q9.label='Safety' 
					MATCH (q10:`GlobalOntology1.2.0`) WHERE q10.label='Security' 
					MATCH (w:`GlobalOntology1.2.0`) WHERE w.label='Active safety' 
					MATCH (w1:`GlobalOntology1.2.0`) WHERE w1.label='Passive safety' 
					MATCH (e:`GlobalOntology1.2.0`) WHERE e.label='Physical security' 
					MATCH (e1:`GlobalOntology1.2.0`) WHERE e1.label='Cyber security' 
					MERGE (n)-[:hasAttribute]->(q)
					MERGE (n)-[:hasAttribute]->(q1)
					MERGE (n)-[:hasAttribute]->(q2)
					MERGE (n)-[:hasAttribute]->(q3)
					MERGE (n)-[:hasAttribute]->(q4)
					MERGE (n)-[:hasAttribute]->(q5)
					MERGE (n)-[:hasAttribute]->(q6)
					MERGE (n)-[:hasAttribute]->(q7)
					MERGE (n)-[:hasAttribute]->(q8)
					MERGE (n)-[:hasAttribute]->(q9)
					MERGE (n)-[:hasAttribute]->(q10) """)
	session.run(""" MATCH (q:`GlobalOntology1.2.0`) WHERE q.label='Road' 
					MATCH (q1:`GlobalOntology1.2.0`) WHERE q1.label='Lane' 
					MATCH (q2:`GlobalOntology1.2.0`) WHERE q2.label='Nature'
					MATCH (q3:`GlobalOntology1.2.0`) WHERE q3.label='Void'
					MATCH (q4:`GlobalOntology1.2.0`) WHERE q4.label='Construction'
					MATCH (q5:`GlobalOntology1.2.0`) WHERE q5.label='Roadside object'    
					MATCH (q6:`GlobalOntology1.2.0`) WHERE q6.label='Road obstacles'
					MATCH (q7:`GlobalOntology1.2.0`) WHERE q7.label='Debris'  
					MERGE (q)<-[:isPartOf]-(q1)
					MERGE (q)<-[:isPartOf]-(q2)
					MERGE (q)<-[:isPartOf]-(q3)
					MERGE (q)<-[:isPartOf]-(q4)
					MERGE (q)<-[:isPartOf]-(q5)
					MERGE (q)<-[:isPartOf]-(q6)
					MERGE (q)<-[:isPartOf]-(q7) """)
	session.run(""" MATCH (q:`GlobalOntology1.2.0`) WHERE q.label='Sidewalk'
					MATCH (q1:`GlobalOntology1.2.0`) WHERE q1.label='Structure'
					MATCH (q2:`GlobalOntology1.2.0`) WHERE q2.label='Barrier'
					MATCH (q3:`GlobalOntology1.2.0`) WHERE q3.label='Bike lane'
					MATCH (q4:`GlobalOntology1.2.0`) WHERE q4.label='Intersection'
					MATCH (q5:`GlobalOntology1.2.0`) WHERE q5.label='Marking'
					MATCH (q6:`GlobalOntology1.2.0`) WHERE q6.label='Footwalk'
					MATCH (q7:`GlobalOntology1.2.0`) WHERE q7.label='Pedestrian area'
					MATCH (q8:`GlobalOntology1.2.0`) WHERE q8.label='Rail track'
					MATCH (q9:`GlobalOntology1.2.0`) WHERE q9.label='Nature'
					MATCH (q10:`GlobalOntology1.2.0`) WHERE q10.label='Movable object'
					MATCH (q11:`GlobalOntology1.2.0`) WHERE q11.label='Roadside object'
					MATCH (q12:`GlobalOntology1.2.0`) WHERE q12.label='Road vehicle'
					MERGE (q)<-[:isPartOf]-(q1)
					MERGE (q)<-[:isPartOf]-(q2)
					MERGE (q)<-[:isPartOf]-(q3)
					MERGE (q)<-[:isPartOf]-(q4)
					MERGE (q)<-[:isPartOf]-(q5)
					MERGE (q)<-[:isPartOf]-(q6)
					MERGE (q)<-[:isPartOf]-(q7)
					MERGE (q)<-[:isPartOf]-(q8)
					MERGE (q)<-[:isPartOf]-(q9)
					MERGE (q)<-[:isPartOf]-(q10)
					MERGE (q)<-[:isPartOf]-(q11)
					MERGE (q)<-[:isPartOf]-(q12) """)
	session.run(""" MATCH (q:`GlobalOntology1.2.0`) WHERE q.label='Pedestrian area'
					MATCH (q1:`GlobalOntology1.2.0`) WHERE q1.label='Structure'
					MATCH (q2:`GlobalOntology1.2.0`) WHERE q2.label='Barrier'
					MATCH (q3:`GlobalOntology1.2.0`) WHERE q3.label='Bike lane'
					MATCH (q4:`GlobalOntology1.2.0`) WHERE q4.label='Intersection'
					MATCH (q5:`GlobalOntology1.2.0`) WHERE q5.label='Marking'
					MATCH (q6:`GlobalOntology1.2.0`) WHERE q6.label='Footwalk'
					MATCH (q7:`GlobalOntology1.2.0`) WHERE q7.label='Nature'
					MATCH (q8:`GlobalOntology1.2.0`) WHERE q8.label='Movable object'
					MATCH (q9:`GlobalOntology1.2.0`) WHERE q9.label='Roadside object'
					MATCH (q10:`GlobalOntology1.2.0`) WHERE q10.label='Cycle'
					MERGE (q)<-[:isPartOf]-(q1)
					MERGE (q)<-[:isPartOf]-(q2)
					MERGE (q)<-[:isPartOf]-(q3)
					MERGE (q)<-[:isPartOf]-(q4)
					MERGE (q)<-[:isPartOf]-(q5)
					MERGE (q)<-[:isPartOf]-(q6)
					MERGE (q)<-[:isPartOf]-(q7)
					MERGE (q)<-[:isPartOf]-(q8)
					MERGE (q)<-[:isPartOf]-(q9)
					MERGE (q)<-[:isPartOf]-(q10) """)				
	session.run(""" MATCH (q:`GlobalOntology1.2.0`) WHERE q.label='Footwalk'
					MATCH (q1:`GlobalOntology1.2.0`) WHERE q1.label='Structure'
					MATCH (q2:`GlobalOntology1.2.0`) WHERE q2.label='Barrier'
					MATCH (q3:`GlobalOntology1.2.0`) WHERE q3.label='Bike lane'
					MATCH (q4:`GlobalOntology1.2.0`) WHERE q4.label='Intersection'
					MATCH (q5:`GlobalOntology1.2.0`) WHERE q5.label='Marking'
					MATCH (q6:`GlobalOntology1.2.0`) WHERE q6.label='Nature'
					MATCH (q7:`GlobalOntology1.2.0`) WHERE q7.label='Movable object'
					MATCH (q8:`GlobalOntology1.2.0`) WHERE q8.label='Roadside object'
					MATCH (q9:`GlobalOntology1.2.0`) WHERE q9.label='Cycle'
					MERGE (q)<-[:isPartOf]-(q1)
					MERGE (q)<-[:isPartOf]-(q2)
					MERGE (q)<-[:isPartOf]-(q3)
					MERGE (q)<-[:isPartOf]-(q4)
					MERGE (q)<-[:isPartOf]-(q5)
					MERGE (q)<-[:isPartOf]-(q6)
					MERGE (q)<-[:isPartOf]-(q7)
					MERGE (q)<-[:isPartOf]-(q8)
					MERGE (q)<-[:isPartOf]-(q9) """)
	session.run(""" MATCH (q:`GlobalOntology1.2.0`) WHERE q.label='Parking'
					MATCH (q1:`GlobalOntology1.2.0`) WHERE q1.label='Structure'
					MATCH (q2:`GlobalOntology1.2.0`) WHERE q2.label='Barrier'
					MATCH (q3:`GlobalOntology1.2.0`) WHERE q3.label='Marking'
					MATCH (q4:`GlobalOntology1.2.0`) WHERE q4.label='Nature'
					MATCH (q5:`GlobalOntology1.2.0`) WHERE q5.label='Movable object'
					MATCH (q6:`GlobalOntology1.2.0`) WHERE q6.label='Roadside object'
					MATCH (q7:`GlobalOntology1.2.0`) WHERE q7.label='Road vehicle'
					MERGE (q)<-[:isPartOf]-(q1)
					MERGE (q)<-[:isPartOf]-(q2)
					MERGE (q)<-[:isPartOf]-(q3)
					MERGE (q)<-[:isPartOf]-(q4)
					MERGE (q)<-[:isPartOf]-(q5)
					MERGE (q)<-[:isPartOf]-(q6)
					MERGE (q)<-[:isPartOf]-(q7) """)
	