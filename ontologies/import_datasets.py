#Import automotive dataset taxonomies into Neo4j:

# Neo4j driver session
from neo4j.v1 import GraphDatabase, basic_auth
driver = GraphDatabase.driver("bolt://galtzagorri:7658", auth=basic_auth(user = "neo4j", password = "galtzagorri"), encrypted=False) 

session = driver.session()

with session:
	# nuScenes
	session.run(""" CREATE (n:DatasetOntology) SET n.name='Thing'
					CREATE (m:DatasetOntology:Object:nuScenes) SET m.name='Object'
					CREATE (m1:DatasetOntology:Object:nuScenes) SET m1.name='animal'
					CREATE (m2:DatasetOntology:Object:nuScenes) SET m2.name='human'
					CREATE (m3:DatasetOntology:Object:nuScenes) SET m3.name='movable_object'
					CREATE (m4:DatasetOntology:Object:nuScenes) SET m4.name='vehicle'
					CREATE (m5:DatasetOntology:Object:nuScenes) SET m5.name='static_object'
					CREATE (t:DatasetOntology:Object:nuScenes) SET t.name='pedestrian'
					CREATE (q:DatasetOntology:Object:nuScenes) SET q.name='adult'
					CREATE (q1:DatasetOntology:Object:nuScenes) SET q1.name='child'
					CREATE (q2:DatasetOntology:Object:nuScenes) SET q2.name='construction_worker'
					CREATE (q4:DatasetOntology:Object:nuScenes) SET q4.name='police_officer'
					CREATE (q5:DatasetOntology:Object:nuScenes) SET q5.name='stroller'
					CREATE (q6:DatasetOntology:Object:nuScenes) SET q6.name='wheelchair'
					CREATE (q7:DatasetOntology:Object:nuScenes) SET q7.name='personal_mobility'
					CREATE (w:DatasetOntology:Object:nuScenes) SET w.name='barrier'
					CREATE (w1:DatasetOntology:Object:nuScenes) SET w1.name='debris'
					CREATE (w2:DatasetOntology:Object:nuScenes) SET w2.name='pushable_pullable'
					CREATE (w3:DatasetOntology:Object:nuScenes) SET w3.name='trafficcone'
					CREATE (e1:DatasetOntology:Object:nuScenes) SET e1.name='bus'
					CREATE (e2:DatasetOntology:Object:nuScenes) SET e2.name='car'
					CREATE (e3:DatasetOntology:Object:nuScenes) SET e3.name='construction'
					CREATE (e4:DatasetOntology:Object:nuScenes) SET e4.name='emergency'
					CREATE (e6:DatasetOntology:Object:nuScenes) SET e6.name='trailer'
					CREATE (e7:DatasetOntology:Object:nuScenes) SET e7.name='truck'
					CREATE (p:DatasetOntology:Object:nuScenes) SET p.name='bendy'
					CREATE (p1:DatasetOntology:Object:nuScenes) SET p1.name='rigid'
					CREATE (r:DatasetOntology:Object:nuScenes) SET r.name='ambulance'
					CREATE (r1:DatasetOntology:Object:nuScenes) SET r1.name='police'
					CREATE (y:DatasetOntology:Object:nuScenes) SET y.name='bicycle_rack'
					MERGE (n)<-[:subClassOf]-(m)
					MERGE (m)<-[:subClassOf]-(m1)
					MERGE (m)<-[:subClassOf]-(m2)
					MERGE (m)<-[:subClassOf]-(m3)
					MERGE (m)<-[:subClassOf]-(m4)
					MERGE (m)<-[:subClassOf]-(m5)
					MERGE (m2)<-[:subClassOf]-(t)
					MERGE (t)<-[:subClassOf]-(q)
					MERGE (t)<-[:subClassOf]-(q1)
					MERGE (t)<-[:subClassOf]-(q2)
					MERGE (t)<-[:subClassOf]-(q3)
					MERGE (t)<-[:subClassOf]-(q4)
					MERGE (t)<-[:subClassOf]-(q5)
					MERGE (t)<-[:subClassOf]-(q6)
					MERGE (t)<-[:subClassOf]-(q7)
					MERGE (m3)<-[:subClassOf]-(w)
					MERGE (m3)<-[:subClassOf]-(w1)
					MERGE (m3)<-[:subClassOf]-(w2)
					MERGE (m3)<-[:subClassOf]-(w3)
					MERGE (m4)<-[:subClassOf]-(e1)
					MERGE (m4)<-[:subClassOf]-(e2)
					MERGE (m4)<-[:subClassOf]-(e3)
					MERGE (m4)<-[:subClassOf]-(e4)
					MERGE (m4)<-[:subClassOf]-(e6)
					MERGE (m4)<-[:subClassOf]-(e7)
					MERGE (e1)<-[:subClassOf]-(p)
					MERGE (e1)<-[:subClassOf]-(p1)
					MERGE (e4)<-[:subClassOf]-(r)
					MERGE (e4)<-[:subClassOf]-(r1)
					MERGE (m5)<-[:subClassOf]-(y) """)
	session.run(""" MATCH (m:DatasetOntology:Object:nuScenes) WHERE m.name='vehicle'
					CREATE (q:DatasetOntology:Object:nuScenes) SET q.name='cycle'
					CREATE (t:DatasetOntology:Object:nuScenes) SET t.name='bicycle'
					CREATE (t1:DatasetOntology:Object:nuScenes) SET t1.name='motorcycle'
					MERGE (m)<-[:subClassOf]-(q)
					MERGE (q)<-[:subClassOf]-(t)
					MERGE (q)<-[:subClassOf]-(t1) """)
	session.run(""" MATCH (t:DatasetOntology:Object:nuScenes) WHERE t.name='pedestrian'
					CREATE (n:DatasetOntology:Action:nuScenes) SET n.name='state'
					CREATE (m:DatasetOntology:Action:nuScenes) SET m.name='sitting_lying_down'
					CREATE (m1:DatasetOntology:Action:nuScenes) SET m1.name='standing'
					CREATE (m2:DatasetOntology:Action:nuScenes) SET m2.name='moving'
					MERGE (t)<-[:subClassOf]-(n)
					MERGE (n)<-[:subClassOf]-(m)
					MERGE (n)<-[:subClassOf]-(m1)
					MERGE (n)<-[:subClassOf]-(m2) """)
	session.run(""" MATCH (t1:DatasetOntology:Object:nuScenes) WHERE t1.name='cycle'
					CREATE (n:DatasetOntology:Action:nuScenes) SET n.name='state'
					CREATE (m4:DatasetOntology:Action:nuScenes) SET m4.name='with_rider'
					CREATE (m5:DatasetOntology:Action:nuScenes) SET m5.name='without_rider'
					MERGE (t1)<-[:subClassOf]-(n)
					MERGE (n)<-[:subClassOf]-(m4)
					MERGE (n)<-[:subClassOf]-(m5) """)
	session.run(""" MATCH (t2:DatasetOntology:Object:nuScenes) WHERE t2.name='vehicle'
					CREATE (n:DatasetOntology:Action:nuScenes) SET n.name='state'
					CREATE (m2:DatasetOntology:Action:nuScenes) SET m2.name='moving'
					CREATE (m6:DatasetOntology:Action:nuScenes) SET m6.name='stopped'
					CREATE (m7:DatasetOntology:Action:nuScenes) SET m7.name='parked'
					MERGE (t2)<-[:subClassOf]-(n)
					MERGE (n)<-[:subClassOf]-(m2)
					MERGE (n)<-[:subClassOf]-(m6)
					MERGE (n)<-[:subClassOf]-(m7) """)
	
	# H3D Honda
	session.run(""" MATCH (w:DatasetOntology) where w.name='Thing'
					CREATE (m:DatasetOntology:Object:H3DHonda) SET m.name='Object'
					CREATE (q:DatasetOntology:Object:H3DHonda) SET q.name='Pedestrian'
					CREATE (q1:DatasetOntology:Object:H3DHonda) SET q1.name='Cyclist'
					CREATE (q2:DatasetOntology:Object:H3DHonda) SET q2.name='Truck'
					CREATE (q3:DatasetOntology:Object:H3DHonda) SET q3.name='Misc'
					CREATE (q4:DatasetOntology:Object:H3DHonda) SET q4.name='Animals'
					CREATE (q5:DatasetOntology:Object:H3DHonda) SET q5.name='Motorcyclist'
					CREATE (q6:DatasetOntology:Object:H3DHonda) SET q6.name='Bus'
					MERGE (w)<-[:subClassOf]-(m)
					MERGE (m)<-[:subClassOf]-(q)
					MERGE (m)<-[:subClassOf]-(q1)
					MERGE (m)<-[:subClassOf]-(q2)
					MERGE (m)<-[:subClassOf]-(q3)
					MERGE (m)<-[:subClassOf]-(q4)
					MERGE (m)<-[:subClassOf]-(q5)
					MERGE (m)<-[:subClassOf]-(q6) """)
	# LyftLevel5
	session.run(""" MATCH (w:DatasetOntology) where w.name='Thing'
					CREATE (m:DatasetOntology:Object:LyftLevel5) SET m.name='Object'
					CREATE (q:DatasetOntology:Object:LyftLevel5) SET q.name='animal'
					CREATE (q1:DatasetOntology:Object:LyftLevel5) SET q1.name='bicycle'
					CREATE (q3:DatasetOntology:Object:LyftLevel5) SET q3.name='bus'
					CREATE (q4:DatasetOntology:Object:LyftLevel5) SET q4.name='car'
					CREATE (q5:DatasetOntology:Object:LyftLevel5) SET q5.name='emergency_vehicle'
					CREATE (q6:DatasetOntology:Object:LyftLevel5) SET q6.name='motorcycle'
					CREATE (q7:DatasetOntology:Object:LyftLevel5) SET q7.name='other_vehicle'
					CREATE (q8:DatasetOntology:Object:LyftLevel5) SET q8.name='pedestrian'
					CREATE (q9:DatasetOntology:Object:LyftLevel5) SET q9.name='truck'
					MERGE (w)<-[:subClassOf]-(m)
					MERGE (m)<-[:subClassOf]-(q)
					MERGE (m)<-[:subClassOf]-(q1)
					MERGE (m)<-[:subClassOf]-(q3)
					MERGE (m)<-[:subClassOf]-(q4)
					MERGE (m)<-[:subClassOf]-(q5)
					MERGE (m)<-[:subClassOf]-(q6)
					MERGE (m)<-[:subClassOf]-(q7)
					MERGE (m)<-[:subClassOf]-(q8)
					MERGE (m)<-[:subClassOf]-(q9) """)
	session.run(""" MATCH (t:DatasetOntology:Object:LyftLevel5) WHERE t.name='bus'
					CREATE (n:DatasetOntology:Action:LyftLevel5) SET n.name='state'
					CREATE (z:DatasetOntology:Action:LyftLevel5) SET z.name='is_stationary'
					CREATE (z1:DatasetOntology:Action:LyftLevel5) SET z1.name='object_action_abnormal_or_traffic_violation'
					CREATE (z2:DatasetOntology:Action:LyftLevel5) SET z2.name='object_action_driving_straight_forward'
					CREATE (z3:DatasetOntology:Action:LyftLevel5) SET z3.name='object_action_lane_change_left'
					CREATE (z4:DatasetOntology:Action:LyftLevel5) SET z4.name='object_action_lane_change_right'
					CREATE (z5:DatasetOntology:Action:LyftLevel5) SET z5.name='object_action_left_turn'
					CREATE (z6:DatasetOntology:Action:LyftLevel5) SET z6.name='object_action_loss_of_control'
					CREATE (z7:DatasetOntology:Action:LyftLevel5) SET z7.name='object_action_other_motion'
					CREATE (z8:DatasetOntology:Action:LyftLevel5) SET z8.name='object_action_parked'
					CREATE (z9:DatasetOntology:Action:LyftLevel5) SET z9.name='object_action_reversing'
					CREATE (z10:DatasetOntology:Action:LyftLevel5) SET z10.name='object_action_right_turn'
					CREATE (z11:DatasetOntology:Action:LyftLevel5) SET z11.name='object_action_stopped'
					CREATE (z12:DatasetOntology:Action:LyftLevel5) SET z12.name='object_action_u_turn'
					CREATE (z13:DatasetOntology:Action:LyftLevel5) SET z13.name='object_action_gliding_on_wheels'
					MERGE (t)<-[:subClassOf]-(n)
					MERGE (n)<-[:subClassOf]-(z)
					MERGE (n)<-[:subClassOf]-(z1)
					MERGE (n)<-[:subClassOf]-(z2)
					MERGE (n)<-[:subClassOf]-(z3)
					MERGE (n)<-[:subClassOf]-(z4)
					MERGE (n)<-[:subClassOf]-(z5)
					MERGE (n)<-[:subClassOf]-(z6)
					MERGE (n)<-[:subClassOf]-(z7)
					MERGE (n)<-[:subClassOf]-(z8)
					MERGE (n)<-[:subClassOf]-(z9)
					MERGE (n)<-[:subClassOf]-(z10)
					MERGE (n)<-[:subClassOf]-(z11)
					MERGE (n)<-[:subClassOf]-(z12)
					MERGE (n)<-[:subClassOf]-(z13) """)
	session.run(""" MATCH (t1:DatasetOntology:Object:LyftLevel5) WHERE t1.name='car'
					CREATE (n:DatasetOntology:Action:LyftLevel5) SET n.name='state'
					CREATE (z:DatasetOntology:Action:LyftLevel5) SET z.name='is_stationary'
					CREATE (z1:DatasetOntology:Action:LyftLevel5) SET z1.name='object_action_abnormal_or_traffic_violation'
					CREATE (z2:DatasetOntology:Action:LyftLevel5) SET z2.name='object_action_driving_straight_forward'
					CREATE (z3:DatasetOntology:Action:LyftLevel5) SET z3.name='object_action_lane_change_left'
					CREATE (z4:DatasetOntology:Action:LyftLevel5) SET z4.name='object_action_lane_change_right'
					CREATE (z5:DatasetOntology:Action:LyftLevel5) SET z5.name='object_action_left_turn'
					CREATE (z6:DatasetOntology:Action:LyftLevel5) SET z6.name='object_action_loss_of_control'
					CREATE (z7:DatasetOntology:Action:LyftLevel5) SET z7.name='object_action_other_motion'
					CREATE (z8:DatasetOntology:Action:LyftLevel5) SET z8.name='object_action_parked'
					CREATE (z9:DatasetOntology:Action:LyftLevel5) SET z9.name='object_action_reversing'
					CREATE (z10:DatasetOntology:Action:LyftLevel5) SET z10.name='object_action_right_turn'
					CREATE (z11:DatasetOntology:Action:LyftLevel5) SET z11.name='object_action_stopped'
					CREATE (z12:DatasetOntology:Action:LyftLevel5) SET z12.name='object_action_u_turn'
					CREATE (p:DatasetOntology:Action:LyftLevel5) SET p.name='object_action_gliding_on_wheels'
					MERGE (t1)<-[:subClassOf]-(n)
					MERGE (n)<-[:subClassOf]-(z)
					MERGE (n)<-[:subClassOf]-(z1)
					MERGE (n)<-[:subClassOf]-(z2)
					MERGE (n)<-[:subClassOf]-(z3)
					MERGE (n)<-[:subClassOf]-(z4)
					MERGE (n)<-[:subClassOf]-(z5)
					MERGE (n)<-[:subClassOf]-(z6)
					MERGE (n)<-[:subClassOf]-(z7)
					MERGE (n)<-[:subClassOf]-(z8)
					MERGE (n)<-[:subClassOf]-(z9)
					MERGE (n)<-[:subClassOf]-(z10)
					MERGE (n)<-[:subClassOf]-(z11)
					MERGE (n)<-[:subClassOf]-(z12)
					MERGE (n)<-[:subClassOf]-(p) """)
	session.run(""" MATCH (t2:DatasetOntology:Object:LyftLevel5) WHERE t2.name='emergency_vehicle'
					CREATE (n:DatasetOntology:Action:LyftLevel5) SET n.name='state'
					CREATE (z:DatasetOntology:Action:LyftLevel5) SET z.name='is_stationary'
					CREATE (z1:DatasetOntology:Action:LyftLevel5) SET z1.name='object_action_abnormal_or_traffic_violation'
					CREATE (z2:DatasetOntology:Action:LyftLevel5) SET z2.name='object_action_driving_straight_forward'
					CREATE (z3:DatasetOntology:Action:LyftLevel5) SET z3.name='object_action_lane_change_left'
					CREATE (z4:DatasetOntology:Action:LyftLevel5) SET z4.name='object_action_lane_change_right'
					CREATE (z5:DatasetOntology:Action:LyftLevel5) SET z5.name='object_action_left_turn'
					CREATE (z6:DatasetOntology:Action:LyftLevel5) SET z6.name='object_action_loss_of_control'
					CREATE (z7:DatasetOntology:Action:LyftLevel5) SET z7.name='object_action_other_motion'
					CREATE (z8:DatasetOntology:Action:LyftLevel5) SET z8.name='object_action_parked'
					CREATE (z9:DatasetOntology:Action:LyftLevel5) SET z9.name='object_action_reversing'
					CREATE (z10:DatasetOntology:Action:LyftLevel5) SET z10.name='object_action_right_turn'
					CREATE (z11:DatasetOntology:Action:LyftLevel5) SET z11.name='object_action_stopped'
					CREATE (z12:DatasetOntology:Action:LyftLevel5) SET z12.name='object_action_u_turn'
					CREATE (p:DatasetOntology:Action:LyftLevel5) SET p.name='object_action_gliding_on_wheels'
					MERGE (t2)<-[:subClassOf]-(n)
					MERGE (n)<-[:subClassOf]-(z)
					MERGE (n)<-[:subClassOf]-(z1)
					MERGE (n)<-[:subClassOf]-(z2)
					MERGE (n)<-[:subClassOf]-(z3)
					MERGE (n)<-[:subClassOf]-(z4)
					MERGE (n)<-[:subClassOf]-(z5)
					MERGE (n)<-[:subClassOf]-(z6)
					MERGE (n)<-[:subClassOf]-(z7)
					MERGE (n)<-[:subClassOf]-(z8)
					MERGE (n)<-[:subClassOf]-(z9)
					MERGE (n)<-[:subClassOf]-(z10)
					MERGE (n)<-[:subClassOf]-(z11)
					MERGE (n)<-[:subClassOf]-(z12)
					MERGE (n)<-[:subClassOf]-(p) """)
	session.run(""" MATCH (t3:DatasetOntology:Object:LyftLevel5) WHERE t3.name='motorcycle'
					CREATE (n:DatasetOntology:Action:LyftLevel5) SET n.name='state'
					CREATE (z:DatasetOntology:Action:LyftLevel5) SET z.name='is_stationary'
					CREATE (z1:DatasetOntology:Action:LyftLevel5) SET z1.name='object_action_abnormal_or_traffic_violation'
					CREATE (z2:DatasetOntology:Action:LyftLevel5) SET z2.name='object_action_driving_straight_forward'
					CREATE (z3:DatasetOntology:Action:LyftLevel5) SET z3.name='object_action_lane_change_left'
					CREATE (z4:DatasetOntology:Action:LyftLevel5) SET z4.name='object_action_lane_change_right'
					CREATE (z5:DatasetOntology:Action:LyftLevel5) SET z5.name='object_action_left_turn'
					CREATE (z6:DatasetOntology:Action:LyftLevel5) SET z6.name='object_action_loss_of_control'
					CREATE (z7:DatasetOntology:Action:LyftLevel5) SET z7.name='object_action_other_motion'
					CREATE (z8:DatasetOntology:Action:LyftLevel5) SET z8.name='object_action_parked'
					CREATE (z9:DatasetOntology:Action:LyftLevel5) SET z9.name='object_action_reversing'
					CREATE (z10:DatasetOntology:Action:LyftLevel5) SET z10.name='object_action_right_turn'
					CREATE (z11:DatasetOntology:Action:LyftLevel5) SET z11.name='object_action_stopped'
					CREATE (z12:DatasetOntology:Action:LyftLevel5) SET z12.name='object_action_u_turn'
					CREATE (p:DatasetOntology:Action:LyftLevel5) SET p.name='object_action_gliding_on_wheels'
					MERGE (t3)<-[:subClassOf]-(n)
					MERGE (n)<-[:subClassOf]-(z)
					MERGE (n)<-[:subClassOf]-(z1)
					MERGE (n)<-[:subClassOf]-(z2)
					MERGE (n)<-[:subClassOf]-(z3)
					MERGE (n)<-[:subClassOf]-(z4)
					MERGE (n)<-[:subClassOf]-(z5)
					MERGE (n)<-[:subClassOf]-(z6)
					MERGE (n)<-[:subClassOf]-(z7)
					MERGE (n)<-[:subClassOf]-(z8)
					MERGE (n)<-[:subClassOf]-(z9)
					MERGE (n)<-[:subClassOf]-(z10)
					MERGE (n)<-[:subClassOf]-(z11)
					MERGE (n)<-[:subClassOf]-(z12)
					MERGE (n)<-[:subClassOf]-(p) """)
	session.run(""" MATCH (t4:DatasetOntology:Object:LyftLevel5) WHERE t4.name='other_vehicle'
					CREATE (n:DatasetOntology:Action:LyftLevel5) SET n.name='state'
					CREATE (z:DatasetOntology:Action:LyftLevel5) SET z.name='is_stationary'
					CREATE (z1:DatasetOntology:Action:LyftLevel5) SET z1.name='object_action_abnormal_or_traffic_violation'
					CREATE (z2:DatasetOntology:Action:LyftLevel5) SET z2.name='object_action_driving_straight_forward'
					CREATE (z3:DatasetOntology:Action:LyftLevel5) SET z3.name='object_action_lane_change_left'
					CREATE (z4:DatasetOntology:Action:LyftLevel5) SET z4.name='object_action_lane_change_right'
					CREATE (z5:DatasetOntology:Action:LyftLevel5) SET z5.name='object_action_left_turn'
					CREATE (z6:DatasetOntology:Action:LyftLevel5) SET z6.name='object_action_loss_of_control'
					CREATE (z7:DatasetOntology:Action:LyftLevel5) SET z7.name='object_action_other_motion'
					CREATE (z8:DatasetOntology:Action:LyftLevel5) SET z8.name='object_action_parked'
					CREATE (z9:DatasetOntology:Action:LyftLevel5) SET z9.name='object_action_reversing'
					CREATE (z10:DatasetOntology:Action:LyftLevel5) SET z10.name='object_action_right_turn'
					CREATE (z11:DatasetOntology:Action:LyftLevel5) SET z11.name='object_action_stopped'
					CREATE (z12:DatasetOntology:Action:LyftLevel5) SET z12.name='object_action_u_turn'
					CREATE (p:DatasetOntology:Action:LyftLevel5) SET p.name='object_action_gliding_on_wheels'
					MERGE (t4)<-[:subClassOf]-(n)
					MERGE (n)<-[:subClassOf]-(z)
					MERGE (n)<-[:subClassOf]-(z1)
					MERGE (n)<-[:subClassOf]-(z2)
					MERGE (n)<-[:subClassOf]-(z3)
					MERGE (n)<-[:subClassOf]-(z4)
					MERGE (n)<-[:subClassOf]-(z5)
					MERGE (n)<-[:subClassOf]-(z6)
					MERGE (n)<-[:subClassOf]-(z7)
					MERGE (n)<-[:subClassOf]-(z8)
					MERGE (n)<-[:subClassOf]-(z9)
					MERGE (n)<-[:subClassOf]-(z10)
					MERGE (n)<-[:subClassOf]-(z11)
					MERGE (n)<-[:subClassOf]-(z12)
					MERGE (n)<-[:subClassOf]-(p) """)
	session.run(""" MATCH (t5:DatasetOntology:Object:LyftLevel5) WHERE t5.name='truck'
					CREATE (n:DatasetOntology:Action:LyftLevel5) SET n.name='state'
					CREATE (z:DatasetOntology:Action:LyftLevel5) SET z.name='is_stationary'
					CREATE (z1:DatasetOntology:Action:LyftLevel5) SET z1.name='object_action_abnormal_or_traffic_violation'
					CREATE (z2:DatasetOntology:Action:LyftLevel5) SET z2.name='object_action_driving_straight_forward'
					CREATE (z3:DatasetOntology:Action:LyftLevel5) SET z3.name='object_action_lane_change_left'
					CREATE (z4:DatasetOntology:Action:LyftLevel5) SET z4.name='object_action_lane_change_right'
					CREATE (z5:DatasetOntology:Action:LyftLevel5) SET z5.name='object_action_left_turn'
					CREATE (z6:DatasetOntology:Action:LyftLevel5) SET z6.name='object_action_loss_of_control'
					CREATE (z7:DatasetOntology:Action:LyftLevel5) SET z7.name='object_action_other_motion'
					CREATE (z8:DatasetOntology:Action:LyftLevel5) SET z8.name='object_action_parked'
					CREATE (z9:DatasetOntology:Action:LyftLevel5) SET z9.name='object_action_reversing'
					CREATE (z10:DatasetOntology:Action:LyftLevel5) SET z10.name='object_action_right_turn'
					CREATE (z11:DatasetOntology:Action:LyftLevel5) SET z11.name='object_action_stopped'
					CREATE (z12:DatasetOntology:Action:LyftLevel5) SET z12.name='object_action_u_turn'
					CREATE (p:DatasetOntology:Action:LyftLevel5) SET p.name='object_action_gliding_on_wheels'
					MERGE (t5)<-[:subClassOf]-(n)
					MERGE (n)<-[:subClassOf]-(z)
					MERGE (n)<-[:subClassOf]-(z1)
					MERGE (n)<-[:subClassOf]-(z2)
					MERGE (n)<-[:subClassOf]-(z3)
					MERGE (n)<-[:subClassOf]-(z4)
					MERGE (n)<-[:subClassOf]-(z5)
					MERGE (n)<-[:subClassOf]-(z6)
					MERGE (n)<-[:subClassOf]-(z7)
					MERGE (n)<-[:subClassOf]-(z8)
					MERGE (n)<-[:subClassOf]-(z9)
					MERGE (n)<-[:subClassOf]-(z10)
					MERGE (n)<-[:subClassOf]-(z11)
					MERGE (n)<-[:subClassOf]-(z12)
					MERGE (n)<-[:subClassOf]-(p) """)
	session.run(""" MATCH (t6:DatasetOntology:Object:LyftLevel5) WHERE t6.name='bicycle'
					CREATE (n:DatasetOntology:Action:LyftLevel5) SET n.name='state'
					CREATE (z:DatasetOntology:Action:LyftLevel5) SET z.name='is_stationary'
					CREATE (z1:DatasetOntology:Action:LyftLevel5) SET z1.name='object_action_abnormal_or_traffic_violation'
					CREATE (z2:DatasetOntology:Action:LyftLevel5) SET z2.name='object_action_driving_straight_forward'
					CREATE (z3:DatasetOntology:Action:LyftLevel5) SET z3.name='object_action_lane_change_left'
					CREATE (z4:DatasetOntology:Action:LyftLevel5) SET z4.name='object_action_lane_change_right'
					CREATE (z5:DatasetOntology:Action:LyftLevel5) SET z5.name='object_action_left_turn'
					CREATE (z6:DatasetOntology:Action:LyftLevel5) SET z6.name='object_action_loss_of_control'
					CREATE (z7:DatasetOntology:Action:LyftLevel5) SET z7.name='object_action_other_motion'
					CREATE (z8:DatasetOntology:Action:LyftLevel5) SET z8.name='object_action_parked'
					CREATE (z9:DatasetOntology:Action:LyftLevel5) SET z9.name='object_action_reversing'
					CREATE (z10:DatasetOntology:Action:LyftLevel5) SET z10.name='object_action_right_turn'
					CREATE (z11:DatasetOntology:Action:LyftLevel5) SET z11.name='object_action_stopped'
					CREATE (z12:DatasetOntology:Action:LyftLevel5) SET z12.name='object_action_u_turn'
					CREATE (p:DatasetOntology:Action:LyftLevel5) SET p.name='object_action_gliding_on_wheels'
					MERGE (t6)<-[:subClassOf]-(n)
					MERGE (n)<-[:subClassOf]-(z)
					MERGE (n)<-[:subClassOf]-(z1)
					MERGE (n)<-[:subClassOf]-(z2)
					MERGE (n)<-[:subClassOf]-(z3)
					MERGE (n)<-[:subClassOf]-(z4)
					MERGE (n)<-[:subClassOf]-(z5)
					MERGE (n)<-[:subClassOf]-(z6)
					MERGE (n)<-[:subClassOf]-(z7)
					MERGE (n)<-[:subClassOf]-(z8)
					MERGE (n)<-[:subClassOf]-(z9)
					MERGE (n)<-[:subClassOf]-(z10)
					MERGE (n)<-[:subClassOf]-(z11)
					MERGE (n)<-[:subClassOf]-(z12)
					MERGE (n)<-[:subClassOf]-(p) """)
	session.run(""" MATCH (c:DatasetOntology:Object:LyftLevel5) WHERE c.name='pedestrian'
					CREATE (n:DatasetOntology:Action:LyftLevel5) SET n.name='state'
					CREATE (z:DatasetOntology:Action:LyftLevel5) SET z.name='is_stationary'
					CREATE (z1:DatasetOntology:Action:LyftLevel5) SET z1.name='object_action_abnormal_or_traffic_violation'
					CREATE (z7:DatasetOntology:Action:LyftLevel5) SET z7.name='object_action_other_motion'
					CREATE (p:DatasetOntology:Action:LyftLevel5) SET p.name='object_action_gliding_on_wheels'
					CREATE (p1:DatasetOntology:Action:LyftLevel5) SET p1.name='object_action_running'
					CREATE (p2:DatasetOntology:Action:LyftLevel5) SET p2.name='object_action_sitting'
					CREATE (p3:DatasetOntology:Action:LyftLevel5) SET p3.name='object_action_standing'
					CREATE (p4:DatasetOntology:Action:LyftLevel5) SET p4.name='object_action_walking'
					MERGE (c)<-[:subClassOf]-(n)
					MERGE (n)<-[:subClassOf]-(z)
					MERGE (n)<-[:subClassOf]-(z1)
					MERGE (n)<-[:subClassOf]-(z7)
					MERGE (n)<-[:subClassOf]-(p)
					MERGE (n)<-[:subClassOf]-(p1)
					MERGE (n)<-[:subClassOf]-(p2)
					MERGE (n)<-[:subClassOf]-(p3)
					MERGE (n)<-[:subClassOf]-(p4) """)
	session.run(""" MATCH (q:DatasetOntology:Object:LyftLevel5) WHERE q.name='animal'
					CREATE (n:DatasetOntology:Action:LyftLevel5) SET n.name='state'
					CREATE (z:DatasetOntology:Action:LyftLevel5) SET z.name='is_stationary'
					CREATE (z7:DatasetOntology:Action:LyftLevel5) SET z7.name='object_action_other_motion'
					CREATE (p1:DatasetOntology:Action:LyftLevel5) SET p1.name='object_action_running'
					CREATE (p2:DatasetOntology:Action:LyftLevel5) SET p2.name='object_action_sitting'
					CREATE (p3:DatasetOntology:Action:LyftLevel5) SET p3.name='object_action_standing'
					CREATE (p4:DatasetOntology:Action:LyftLevel5) SET p4.name='object_action_walking'
					MERGE (q)<-[:subClassOf]-(n)
					MERGE (n)<-[:subClassOf]-(z)
					MERGE (n)<-[:subClassOf]-(z7)
					MERGE (n)<-[:subClassOf]-(p1)
					MERGE (n)<-[:subClassOf]-(p2)
					MERGE (n)<-[:subClassOf]-(p3)
					MERGE (n)<-[:subClassOf]-(p4) """)
	
	# Waymo
	session.run(""" MATCH (w:DatasetOntology) where w.name='Thing'
					CREATE (m:DatasetOntology:Object:Waymo) SET m.name='Object'
					CREATE (q:DatasetOntology:Object:Waymo) SET q.name='Vehicles'
					CREATE (q1:DatasetOntology:Object:Waymo) SET q1.name='Pedestrians'
					CREATE (q2:DatasetOntology:Object:Waymo) SET q2.name='Cyclists'
					CREATE (q3:DatasetOntology:Object:Waymo) SET q3.name='Signs'
					MERGE (w)<-[:subClassOf]-(m)
					MERGE (m)<-[:subClassOf]-(q)
					MERGE (m)<-[:subClassOf]-(q1)
					MERGE (m)<-[:subClassOf]-(q2)
					MERGE (m)<-[:subClassOf]-(q3) """)
	
	# Audi A2-D2
	session.run(""" MATCH (w:DatasetOntology) where w.name='Thing'
					CREATE (m:DatasetOntology:Object:AudiA2D2) SET m.name='Object'
					CREATE (q:DatasetOntology:Object:AudiA2D2) SET q.name='Car'
					CREATE (q1:DatasetOntology:Object:AudiA2D2) SET q1.name='Bicycle'
					CREATE (q2:DatasetOntology:Object:AudiA2D2) SET q2.name='Pedestrian'
					CREATE (q3:DatasetOntology:Object:AudiA2D2) SET q3.name='Truck'
					CREATE (q4:DatasetOntology:Object:AudiA2D2) SET q4.name='Small Vehicle'
					CREATE (q5:DatasetOntology:Object:AudiA2D2) SET q5.name='Traffic signal'
					CREATE (q6:DatasetOntology:Object:AudiA2D2) SET q6.name='Traffic sign'
					CREATE (q7:DatasetOntology:Object:AudiA2D2) SET q7.name='Utility vehicle'
					CREATE (q8:DatasetOntology:Object:AudiA2D2) SET q8.name='Sidebars'
					CREATE (q9:DatasetOntology:Object:AudiA2D2) SET q9.name='Speed bumper'
					CREATE (q10:DatasetOntology:Object:AudiA2D2) SET q10.name='curbstone'
					CREATE (q11:DatasetOntology:Object:AudiA2D2) SET q11.name='Solid line'
					CREATE (q12:DatasetOntology:Object:AudiA2D2) SET q12.name='Irrelevant signs'
					CREATE (q13:DatasetOntology:Object:AudiA2D2) SET q13.name='Road blocks'
					CREATE (q14:DatasetOntology:Object:AudiA2D2) SET q14.name='Tractor'
					CREATE (q15:DatasetOntology:Object:AudiA2D2) SET q15.name='Non-drivable street'
					CREATE (q16:DatasetOntology:Object:AudiA2D2) SET q16.name='Zebra crossing'
					CREATE (q17:DatasetOntology:Object:AudiA2D2) SET q17.name='Obstacles'
					CREATE (q18:DatasetOntology:Object:AudiA2D2) SET q18.name='Trash'
					CREATE (q19:DatasetOntology:Object:AudiA2D2) SET q19.name='Poles'
					CREATE (q20:DatasetOntology:Object:AudiA2D2) SET q20.name='RD restricted area'
					CREATE (q21:DatasetOntology:Object:AudiA2D2) SET q21.name='Animals'
					CREATE (q22:DatasetOntology:Object:AudiA2D2) SET q22.name='Grid structure'
					CREATE (q23:DatasetOntology:Object:AudiA2D2) SET q23.name='Signal corpus'
					CREATE (q24:DatasetOntology:Object:AudiA2D2) SET q24.name='Drivable cobblestone'
					CREATE (q25:DatasetOntology:Object:AudiA2D2) SET q25.name='Electronic traffic'
					CREATE (q26:DatasetOntology:Object:AudiA2D2) SET q26.name='Slow drive area'
					CREATE (q27:DatasetOntology:Object:AudiA2D2) SET q27.name='Nature object'
					CREATE (q28:DatasetOntology:Object:AudiA2D2) SET q28.name='Parking Area'
					CREATE (q29:DatasetOntology:Object:AudiA2D2) SET q29.name='Sidewalk'
					CREATE (q30:DatasetOntology:Object:AudiA2D2) SET q30.name='Ego car'
					CREATE (q31:DatasetOntology:Object:AudiA2D2) SET q31.name='Painted driv. instr.'
					CREATE (q32:DatasetOntology:Object:AudiA2D2) SET q32.name='Traffic guide obj'
					CREATE (q33:DatasetOntology:Object:AudiA2D2) SET q33.name='dashed line'
					CREATE (q34:DatasetOntology:Object:AudiA2D2) SET q34.name='RD normal street'
					CREATE (q35:DatasetOntology:Object:AudiA2D2) SET q35.name='Sky'
					CREATE (q36:DatasetOntology:Object:AudiA2D2) SET q36.name='Buildings'
					CREATE (q37:DatasetOntology:Object:AudiA2D2) SET q37.name='Blurred area'
					CREATE (q38:DatasetOntology:Object:AudiA2D2) SET q38.name='Rain dirt'
					CREATE (r:DatasetOntology:Object:AudiA2D2) SET r.name='VanSUV'
					CREATE (r1:DatasetOntology:Object:AudiA2D2) SET r1.name='Motorcycle'
					CREATE (r2:DatasetOntology:Object:AudiA2D2) SET r2.name='MotorBiker'
					CREATE (r3:DatasetOntology:Object:AudiA2D2) SET r3.name='Bicycle'
					CREATE (r4:DatasetOntology:Object:AudiA2D2) SET r4.name='UtilityVehicle'
					CREATE (r5:DatasetOntology:Object:AudiA2D2) SET r5.name='Bus'
					CREATE (r6:DatasetOntology:Object:AudiA2D2) SET r6.name='Cyclist'
					CREATE (r7:DatasetOntology:Object:AudiA2D2) SET r7.name='Trailer'
					CREATE (r8:DatasetOntology:Object:AudiA2D2) SET r8.name='CaravanTransporter'
					CREATE (r9:DatasetOntology:Object:AudiA2D2) SET r9.name='Animal'
					CREATE (r10:DatasetOntology:Object:AudiA2D2) SET r10.name='EmergencyVehicle'
					MERGE (w)<-[:subClassOf]-(m)
					MERGE (m)<-[:subClassOf]-(q)
					MERGE (m)<-[:subClassOf]-(q1)
					MERGE (m)<-[:subClassOf]-(q2)
					MERGE (m)<-[:subClassOf]-(q3)
					MERGE (m)<-[:subClassOf]-(q4)
					MERGE (m)<-[:subClassOf]-(q5)
					MERGE (m)<-[:subClassOf]-(q6)
					MERGE (m)<-[:subClassOf]-(q7)
					MERGE (m)<-[:subClassOf]-(q8)
					MERGE (m)<-[:subClassOf]-(q9)
					MERGE (m)<-[:subClassOf]-(q10)
					MERGE (m)<-[:subClassOf]-(q11)
					MERGE (m)<-[:subClassOf]-(q12)
					MERGE (m)<-[:subClassOf]-(q13)
					MERGE (m)<-[:subClassOf]-(q14)
					MERGE (m)<-[:subClassOf]-(q15)
					MERGE (m)<-[:subClassOf]-(q16)
					MERGE (m)<-[:subClassOf]-(q17)
					MERGE (m)<-[:subClassOf]-(q18)
					MERGE (q17)<-[:sameAs]-(q18)
					MERGE (m)<-[:subClassOf]-(q19)
					MERGE (m)<-[:subClassOf]-(q20)
					MERGE (m)<-[:subClassOf]-(q21)
					MERGE (m)<-[:subClassOf]-(q22)
					MERGE (m)<-[:subClassOf]-(q23)
					MERGE (m)<-[:subClassOf]-(q24)
					MERGE (m)<-[:subClassOf]-(q25)
					MERGE (m)<-[:subClassOf]-(q26)
					MERGE (m)<-[:subClassOf]-(q27)
					MERGE (m)<-[:subClassOf]-(q28)
					MERGE (m)<-[:subClassOf]-(q29)
					MERGE (m)<-[:subClassOf]-(q30)
					MERGE (m)<-[:subClassOf]-(q31)
					MERGE (m)<-[:subClassOf]-(q32)
					MERGE (m)<-[:subClassOf]-(q33)
					MERGE (m)<-[:subClassOf]-(q34)
					MERGE (m)<-[:subClassOf]-(q35)
					MERGE (m)<-[:subClassOf]-(q36)
					MERGE (m)<-[:subClassOf]-(q37)
					MERGE (m)<-[:subClassOf]-(q38)
					MERGE (m)<-[:subClassOf]-(r)
					MERGE (m)<-[:subClassOf]-(r2)
					MERGE (m)<-[:subClassOf]-(r3)
					MERGE (m)<-[:subClassOf]-(r4)
					MERGE (m)<-[:subClassOf]-(r5)
					MERGE (m)<-[:subClassOf]-(r6)
					MERGE (m)<-[:subClassOf]-(r7)
					MERGE (m)<-[:subClassOf]-(r8)
					MERGE (m)<-[:subClassOf]-(r9)
					MERGE (m)<-[:subClassOf]-(r10) """)
	
	# Berkeley Deep-Drive
	session.run(""" MATCH (w:DatasetOntology) where w.name='Thing'
					CREATE (m:DatasetOntology:Object:Berkeley) SET m.name='Void'
					CREATE (m1:DatasetOntology:Object:Berkeley) SET m1.name='Flat'
					CREATE (m2:DatasetOntology:Object:Berkeley) SET m2.name='Construction'
					CREATE (m3:DatasetOntology:Object:Berkeley) SET m3.name='Object'
					CREATE (m4:DatasetOntology:Object:Berkeley) SET m4.name='Nature'
					CREATE (m5:DatasetOntology:Object:Berkeley) SET m5.name='Sky'
					CREATE (m6:DatasetOntology:Object:Berkeley) SET m6.name='Human'
					CREATE (m7:DatasetOntology:Object:Berkeley) SET m7.name='Vehicle'
					CREATE (q:DatasetOntology:Object:Berkeley) SET q.name='Unlabeled'
					CREATE (q1:DatasetOntology:Object:Berkeley) SET q1.name='Dynamic'
					CREATE (q2:DatasetOntology:Object:Berkeley) SET q2.name='Ego vehicle'
					CREATE (q3:DatasetOntology:Object:Berkeley) SET q3.name='Ground'
					CREATE (q4:DatasetOntology:Object:Berkeley) SET q4.name='Static'
					CREATE (e:DatasetOntology:Object:Berkeley) SET e.name='Parking'
					CREATE (e1:DatasetOntology:Object:Berkeley) SET e1.name='Rail track'
					CREATE (e2:DatasetOntology:Object:Berkeley) SET e2.name='Road'
					CREATE (e3:DatasetOntology:Object:Berkeley) SET e3.name='Sidewalk'
					CREATE (r:DatasetOntology:Object:Berkeley) SET r.name='Bridge'
					CREATE (r1:DatasetOntology:Object:Berkeley) SET r1.name='Building'
					CREATE (r2:DatasetOntology:Object:Berkeley) SET r2.name='Fence'
					CREATE (r3:DatasetOntology:Object:Berkeley) SET r3.name='Garage'
					CREATE (r4:DatasetOntology:Object:Berkeley) SET r4.name='Guard rail'
					CREATE (r5:DatasetOntology:Object:Berkeley) SET r5.name='Tunnel'
					CREATE (r6:DatasetOntology:Object:Berkeley) SET r6.name='Wall'
					CREATE (t:DatasetOntology:Object:Berkeley) SET t.name='Banner'
					CREATE (t1:DatasetOntology:Object:Berkeley) SET t1.name='Billboard'
					CREATE (t2:DatasetOntology:Object:Berkeley) SET t2.name='Lane divider'
					CREATE (t3:DatasetOntology:Object:Berkeley) SET t3.name='Parking Sign'
					CREATE (t4:DatasetOntology:Object:Berkeley) SET t4.name='Pole'
					CREATE (t5:DatasetOntology:Object:Berkeley) SET t5.name='Polegroup'
					CREATE (t6:DatasetOntology:Object:Berkeley) SET t6.name='Street light'
					CREATE (t7:DatasetOntology:Object:Berkeley) SET t7.name='Traffic cone'
					CREATE (t8:DatasetOntology:Object:Berkeley) SET t8.name='Traffic device'
					CREATE (t9:DatasetOntology:Object:Berkeley) SET t9.name='Traffic light'
					CREATE (t10:DatasetOntology:Object:Berkeley) SET t10.name='Traffic sign'
					CREATE (t11:DatasetOntology:Object:Berkeley) SET t11.name='Traffic sign frame'
					CREATE (y:DatasetOntology:Object:Berkeley) SET y.name='Terrain'
					CREATE (y1:DatasetOntology:Object:Berkeley) SET y1.name='Vegetation'
					CREATE (u:DatasetOntology:Object:Berkeley) SET u.name='Person'
					CREATE (u1:DatasetOntology:Object:Berkeley) SET u1.name='Rider'
					CREATE (a:DatasetOntology:Object:Berkeley) SET a.name='Bicycle'
					CREATE (a1:DatasetOntology:Object:Berkeley) SET a1.name='Bus'
					CREATE (a2:DatasetOntology:Object:Berkeley) SET a2.name='Car'
					CREATE (a3:DatasetOntology:Object:Berkeley) SET a3.name='Caravan'
					CREATE (a4:DatasetOntology:Object:Berkeley) SET a4.name='Motorcycle'
					CREATE (a5:DatasetOntology:Object:Berkeley) SET a5.name='Trailer'
					CREATE (a6:DatasetOntology:Object:Berkeley) SET a6.name='Train'
					CREATE (a7:DatasetOntology:Object:Berkeley) SET a7.name='Truck'
					MERGE (w)<-[:subClassOf]-(m)
					MERGE (w)<-[:subClassOf]-(m1)
					MERGE (w)<-[:subClassOf]-(m2)
					MERGE (w)<-[:subClassOf]-(m3)
					MERGE (w)<-[:subClassOf]-(m4)
					MERGE (w)<-[:subClassOf]-(m5)
					MERGE (w)<-[:subClassOf]-(m6)
					MERGE (w)<-[:subClassOf]-(m7)
					MERGE (m)<-[:subClassOf]-(q)
					MERGE (m)<-[:subClassOf]-(q1)
					MERGE (m)<-[:subClassOf]-(q2)
					MERGE (m)<-[:subClassOf]-(q3)
					MERGE (m)<-[:subClassOf]-(q4)
					MERGE (m1)<-[:subClassOf]-(e)
					MERGE (m1)<-[:subClassOf]-(e1)
					MERGE (m1)<-[:subClassOf]-(e2)
					MERGE (m1)<-[:subClassOf]-(e3)
					MERGE (m2)<-[:subClassOf]-(r)
					MERGE (m2)<-[:subClassOf]-(r1)
					MERGE (m2)<-[:subClassOf]-(r2)
					MERGE (m2)<-[:subClassOf]-(r3)
					MERGE (m2)<-[:subClassOf]-(r4)
					MERGE (m2)<-[:subClassOf]-(r5)
					MERGE (m2)<-[:subClassOf]-(r6)
					MERGE (m3)<-[:subClassOf]-(t)
					MERGE (m3)<-[:subClassOf]-(t1)
					MERGE (m3)<-[:subClassOf]-(t2)
					MERGE (m3)<-[:subClassOf]-(t3)
					MERGE (m3)<-[:subClassOf]-(t4)
					MERGE (m3)<-[:subClassOf]-(t5)
					MERGE (m3)<-[:subClassOf]-(t6)
					MERGE (m3)<-[:subClassOf]-(t7)
					MERGE (m3)<-[:subClassOf]-(t8)
					MERGE (m3)<-[:subClassOf]-(t9)
					MERGE (m3)<-[:subClassOf]-(t10)
					MERGE (m3)<-[:subClassOf]-(t11)
					MERGE (m4)<-[:subClassOf]-(y)
					MERGE (m4)<-[:subClassOf]-(y1)
					MERGE (m6)<-[:subClassOf]-(u)
					MERGE (m6)<-[:subClassOf]-(u1)
					MERGE (m7)<-[:subClassOf]-(a)
					MERGE (m7)<-[:subClassOf]-(a1)
					MERGE (m7)<-[:subClassOf]-(a2)
					MERGE (m7)<-[:subClassOf]-(a3)
					MERGE (m7)<-[:subClassOf]-(a4)
					MERGE (m7)<-[:subClassOf]-(a5)
					MERGE (m7)<-[:subClassOf]-(a6)
					MERGE (m7)<-[:subClassOf]-(a7) """)
	
	# Apolloscape
	session.run(""" MATCH (w:DatasetOntology) where w.name='Thing'
					CREATE (m:DatasetOntology:Object:Apolloscape) SET m.name='Others'
					CREATE (m1:DatasetOntology:Object:Apolloscape) SET m1.name='Sky'
					CREATE (m2:DatasetOntology:Object:Apolloscape) SET m2.name='Movable object'
					CREATE (m3:DatasetOntology:Object:Apolloscape) SET m3.name='flat'
					CREATE (m4:DatasetOntology:Object:Apolloscape) SET m4.name='Road obstacles'
					CREATE (m5:DatasetOntology:Object:Apolloscape) SET m5.name='Roadside objects'
					CREATE (m6:DatasetOntology:Object:Apolloscape) SET m6.name='Building'
					CREATE (m7:DatasetOntology:Object:Apolloscape) SET m7.name='Natural'
					CREATE (m8:DatasetOntology:Object:Apolloscape) SET m8.name='Unlabeled'
					CREATE (q:DatasetOntology:Object:Apolloscape) SET q.name='rover'
					CREATE (e:DatasetOntology:Object:Apolloscape) SET e.name='Car'
					CREATE (e1:DatasetOntology:Object:Apolloscape) SET e1.name='Motorbicycle'
					CREATE (e2:DatasetOntology:Object:Apolloscape) SET e2.name='Bicycle'
					CREATE (e3:DatasetOntology:Object:Apolloscape) SET e3.name='Person'
					CREATE (e4:DatasetOntology:Object:Apolloscape) SET e4.name='Rider'
					CREATE (e5:DatasetOntology:Object:Apolloscape) SET e5.name='Truck'
					CREATE (e6:DatasetOntology:Object:Apolloscape) SET e6.name='Bus'
					CREATE (e7:DatasetOntology:Object:Apolloscape) SET e7.name='Tricycle'
					CREATE (r:DatasetOntology:Object:Apolloscape) SET r.name='Road'
					CREATE (r1:DatasetOntology:Object:Apolloscape) SET r1.name='Sidewalk'
					CREATE (t:DatasetOntology:Object:Apolloscape) SET t.name='traffic_cone'
					CREATE (t1:DatasetOntology:Object:Apolloscape) SET t1.name='road_pile'
					CREATE (t2:DatasetOntology:Object:Apolloscape) SET t2.name='Fence'
					CREATE (y:DatasetOntology:Object:Apolloscape) SET y.name='traffic_light'
					CREATE (y1:DatasetOntology:Object:Apolloscape) SET y1.name='pole'
					CREATE (y2:DatasetOntology:Object:Apolloscape) SET y2.name='traffic_sign'
					CREATE (y3:DatasetOntology:Object:Apolloscape) SET y3.name='wall'
					CREATE (y4:DatasetOntology:Object:Apolloscape) SET y4.name='dustbin'
					CREATE (y5:DatasetOntology:Object:Apolloscape) SET y5.name='billboard'
					CREATE (u:DatasetOntology:Object:Apolloscape) SET u.name='Bridge'
					CREATE (u1:DatasetOntology:Object:Apolloscape) SET u1.name='Tunnel'
					CREATE (u2:DatasetOntology:Object:Apolloscape) SET u2.name='Overpass'
					CREATE (a:DatasetOntology:Object:Apolloscape) SET a.name='Vegetation'
					MERGE (w)<-[:subClassOf]-(m)
					MERGE (w)<-[:subClassOf]-(m1)
					MERGE (w)<-[:subClassOf]-(m2)
					MERGE (w)<-[:subClassOf]-(m3)
					MERGE (w)<-[:subClassOf]-(m4)
					MERGE (w)<-[:subClassOf]-(m5)
					MERGE (w)<-[:subClassOf]-(m6)
					MERGE (w)<-[:subClassOf]-(m7)
					MERGE (w)<-[:subClassOf]-(m8)
					MERGE (m)<-[:subClassOf]-(q)
					MERGE (m2)<-[:subClassOf]-(e)
					MERGE (m2)<-[:subClassOf]-(e1)
					MERGE (m2)<-[:subClassOf]-(e2)
					MERGE (m2)<-[:subClassOf]-(e3)
					MERGE (m2)<-[:subClassOf]-(e4)
					MERGE (m2)<-[:subClassOf]-(e5)
					MERGE (m2)<-[:subClassOf]-(e6)
					MERGE (m2)<-[:subClassOf]-(e7)
					MERGE (m3)<-[:subClassOf]-(r)
					MERGE (m3)<-[:subClassOf]-(r1)
					MERGE (m4)<-[:subClassOf]-(t)
					MERGE (m4)<-[:subClassOf]-(t1)
					MERGE (m4)<-[:subClassOf]-(t2)
					MERGE (m5)<-[:subClassOf]-(y)
					MERGE (m5)<-[:subClassOf]-(y1)
					MERGE (m5)<-[:subClassOf]-(y2)
					MERGE (m5)<-[:subClassOf]-(y3)
					MERGE (m5)<-[:subClassOf]-(y4)
					MERGE (m5)<-[:subClassOf]-(y5)
					MERGE (m6)<-[:subClassOf]-(u)
					MERGE (m6)<-[:subClassOf]-(u1)
					MERGE (m6)<-[:subClassOf]-(u2)
					MERGE (m7)<-[:subClassOf]-(a) """)
	session.run(""" MATCH (w:DatasetOntology) where w.name='Thing'
					CREATE (m:DatasetOntology:Object:Apolloscape) SET m.name='Lane marking'
					CREATE (n:DatasetOntology:Object:Apolloscape) SET n.name='Solid-w-dividing'
					CREATE (n1:DatasetOntology:Object:Apolloscape) SET n1.name='Solid-y-dividing'
					CREATE (n2:DatasetOntology:Object:Apolloscape) SET n2.name='DoubleSolid-w-dividing'
					CREATE (n3:DatasetOntology:Object:Apolloscape) SET n3.name='DoubleSolid-y-dividing'
					CREATE (n4:DatasetOntology:Object:Apolloscape) SET n4.name='Solid&broken-w-dividing'
					CREATE (n5:DatasetOntology:Object:Apolloscape) SET n5.name='Solid&broken-y-dividing'
					CREATE (n6:DatasetOntology:Object:Apolloscape) SET n6.name='Broken-w-guiding'
					CREATE (n7:DatasetOntology:Object:Apolloscape) SET n7.name='Broken-y-guiding'
					CREATE (n8:DatasetOntology:Object:Apolloscape) SET n8.name='DoubleBroken-w-guiding'
					CREATE (n9:DatasetOntology:Object:Apolloscape) SET n9.name='DoubleBroken-y-guiding'
					CREATE (n10:DatasetOntology:Object:Apolloscape) SET n10.name='DoubleBroken-w-stop'
					CREATE (n11:DatasetOntology:Object:Apolloscape) SET n11.name='Broken-w-stop'
					CREATE (n12:DatasetOntology:Object:Apolloscape) SET n12.name='Solid-w-chevron'
					CREATE (n13:DatasetOntology:Object:Apolloscape) SET n13.name='Solid-y-chevron'
					CREATE (n14:DatasetOntology:Object:Apolloscape) SET n14.name='Solid-w-parking'
					CREATE (n15:DatasetOntology:Object:Apolloscape) SET n15.name='Crosswalk-w-parallel'
					CREATE (n16:DatasetOntology:Object:Apolloscape) SET n16.name='Crosswalk-w-zebra'
					CREATE (n17:DatasetOntology:Object:Apolloscape) SET n17.name='Arrow-w-rightTurn'
					CREATE (n18:DatasetOntology:Object:Apolloscape) SET n18.name='Arrow-w-leftTurn'
					CREATE (n19:DatasetOntology:Object:Apolloscape) SET n19.name='Arrow-w-thru&rightTurn'
					CREATE (n20:DatasetOntology:Object:Apolloscape) SET n20.name='Arrow-w-thru&leftTurn'
					CREATE (n21:DatasetOntology:Object:Apolloscape) SET n21.name='Arrow-w-thru'
					CREATE (n22:DatasetOntology:Object:Apolloscape) SET n22.name='Arrow-w-uTurn'
					CREATE (n23:DatasetOntology:Object:Apolloscape) SET n23.name='Arrow-w-left&rightTurn'
					CREATE (n24:DatasetOntology:Object:Apolloscape) SET n24.name='Symbol-w-restricted'
					CREATE (n25:DatasetOntology:Object:Apolloscape) SET n25.name='bump-n'
					CREATE (n26:DatasetOntology:Object:Apolloscape) SET n26.name='a-speedReduction'
					CREATE (n27:DatasetOntology:Object:Apolloscape) SET n27.name='visibleOldMarking-yw-n'
					CREATE (n28:DatasetOntology:Object:Apolloscape) SET n28.name='visibleOldMarking-yw-a'
					CREATE (n29:DatasetOntology:Object:Apolloscape) SET n29.name='void-void-otherUnlabeled'
					MERGE (w)<-[:subClassOf]-(m)
					MERGE (m)<-[:subClassOf]-(n)
					MERGE (m)<-[:subClassOf]-(n1)
					MERGE (m)<-[:subClassOf]-(n2)
					MERGE (m)<-[:subClassOf]-(n3)
					MERGE (m)<-[:subClassOf]-(n4)
					MERGE (m)<-[:subClassOf]-(n5)
					MERGE (m)<-[:subClassOf]-(n6)
					MERGE (m)<-[:subClassOf]-(n7)
					MERGE (m)<-[:subClassOf]-(n8)
					MERGE (m)<-[:subClassOf]-(n9)
					MERGE (m)<-[:subClassOf]-(n10)
					MERGE (m)<-[:subClassOf]-(n11)
					MERGE (m)<-[:subClassOf]-(n12)
					MERGE (m)<-[:subClassOf]-(n13)
					MERGE (m)<-[:subClassOf]-(n14)
					MERGE (m)<-[:subClassOf]-(n15)
					MERGE (m)<-[:subClassOf]-(n16)
					MERGE (m)<-[:subClassOf]-(n17)
					MERGE (m)<-[:subClassOf]-(n18)
					MERGE (m)<-[:subClassOf]-(n19)
					MERGE (m)<-[:subClassOf]-(n20)
					MERGE (m)<-[:subClassOf]-(n21)
					MERGE (m)<-[:subClassOf]-(n22)
					MERGE (m)<-[:subClassOf]-(n23)
					MERGE (m)<-[:subClassOf]-(n24)
					MERGE (m)<-[:subClassOf]-(n25)
					MERGE (m)<-[:subClassOf]-(n26)
					MERGE (n25)<-[:sameAs]-(n26)
					MERGE (m)<-[:subClassOf]-(n27)
					MERGE (m)<-[:subClassOf]-(n28)
					MERGE (n27)<-[:sameAs]-(n28)
					MERGE (m)<-[:subClassOf]-(n29) """)
	
	# Mapillary-Vistas
	session.run(""" MATCH (w:DatasetOntology) where w.name='Thing'
					CREATE (m:DatasetOntology:Object:Mapillary) SET m.name='Object'
					CREATE (m1:DatasetOntology:Object:Mapillary) SET m1.name='Construction'
					CREATE (m2:DatasetOntology:Object:Mapillary) SET m2.name='Human'
					CREATE (m3:DatasetOntology:Object:Mapillary) SET m3.name='Marking'
					CREATE (m4:DatasetOntology:Object:Mapillary) SET m4.name='Nature'
					CREATE (m5:DatasetOntology:Object:Mapillary) SET m5.name='Void'
					CREATE (m6:DatasetOntology:Object:Mapillary) SET m6.name='Animal'
					CREATE (n:DatasetOntology:Object:Mapillary) SET n.name='support'
					CREATE (q:DatasetOntology:Object:Mapillary) SET q.name='pole'
					CREATE (q1:DatasetOntology:Object:Mapillary) SET q1.name='utility-pole'
					CREATE (q2:DatasetOntology:Object:Mapillary) SET q2.name='traffic-sign-frame'
					CREATE (n1:DatasetOntology:Object:Mapillary) SET n1.name='street-light'
					CREATE (n2:DatasetOntology:Object:Mapillary) SET n2.name='billboard'
					CREATE (n3:DatasetOntology:Object:Mapillary) SET n3.name='traffic-light'
					CREATE (n4:DatasetOntology:Object:Mapillary) SET n4.name='manhole'
					CREATE (n5:DatasetOntology:Object:Mapillary) SET n5.name='banner'
					CREATE (n6:DatasetOntology:Object:Mapillary) SET n6.name='trash-can'
					CREATE (n7:DatasetOntology:Object:Mapillary) SET n7.name='catch-basin'
					CREATE (n8:DatasetOntology:Object:Mapillary) SET n8.name='junction-box'
					CREATE (n9:DatasetOntology:Object:Mapillary) SET n9.name='cctv-camera'
					CREATE (n10:DatasetOntology:Object:Mapillary) SET n10.name='fire-hydrant'
					CREATE (n11:DatasetOntology:Object:Mapillary) SET n11.name='bench'
					CREATE (n12:DatasetOntology:Object:Mapillary) SET n12.name='bike-rack'
					CREATE (n13:DatasetOntology:Object:Mapillary) SET n13.name='mailbox'
					CREATE (n14:DatasetOntology:Object:Mapillary) SET n14.name='pothole'
					CREATE (n15:DatasetOntology:Object:Mapillary) SET n15.name='phone-booth'
					CREATE (n16:DatasetOntology:Object:Mapillary) SET n16.name='vehicle'
					CREATE (z:DatasetOntology:Object:Mapillary) SET z.name='car'
					CREATE (z1:DatasetOntology:Object:Mapillary) SET z1.name='truck'
					CREATE (z2:DatasetOntology:Object:Mapillary) SET z2.name='bicycle'
					CREATE (z3:DatasetOntology:Object:Mapillary) SET z3.name='motorcycle'
					CREATE (z4:DatasetOntology:Object:Mapillary) SET z4.name='bus'
					CREATE (z5:DatasetOntology:Object:Mapillary) SET z5.name='other-vehicle'
					CREATE (z6:DatasetOntology:Object:Mapillary) SET z6.name='wheeled-slow'
					CREATE (z7:DatasetOntology:Object:Mapillary) SET z7.name='boat'
					CREATE (z8:DatasetOntology:Object:Mapillary) SET z8.name='on-rails'
					CREATE (z9:DatasetOntology:Object:Mapillary) SET z9.name='trailer'
					CREATE (z10:DatasetOntology:Object:Mapillary) SET z10.name='caravan'
					CREATE (n17:DatasetOntology:Object:Mapillary) SET n17.name='traffic-sign'
					CREATE (x:DatasetOntology:Object:Mapillary) SET x.name='front'
					CREATE (x1:DatasetOntology:Object:Mapillary) SET x1.name='back'
					CREATE (c:DatasetOntology:Object:Mapillary) SET c.name='flat'
					CREATE (v:DatasetOntology:Object:Mapillary) SET v.name='road'
					CREATE (v1:DatasetOntology:Object:Mapillary) SET v1.name='sidewalk'
					CREATE (v2:DatasetOntology:Object:Mapillary) SET v2.name='curb-cut'
					CREATE (v3:DatasetOntology:Object:Mapillary) SET v3.name='crosswalk-plain'
					CREATE (v4:DatasetOntology:Object:Mapillary) SET v4.name='parking'
					CREATE (v5:DatasetOntology:Object:Mapillary) SET v5.name='bike-lane'
					CREATE (v6:DatasetOntology:Object:Mapillary) SET v6.name='service-lane'
					CREATE (v7:DatasetOntology:Object:Mapillary) SET v7.name='rail-track'
					CREATE (v8:DatasetOntology:Object:Mapillary) SET v8.name='pedestrian-area'
					CREATE (c1:DatasetOntology:Object:Mapillary) SET c1.name='barrier'
					CREATE (b:DatasetOntology:Object:Mapillary) SET b.name='curb'
					CREATE (b1:DatasetOntology:Object:Mapillary) SET b1.name='fence'
					CREATE (b2:DatasetOntology:Object:Mapillary) SET b2.name='wall'
					CREATE (b3:DatasetOntology:Object:Mapillary) SET b3.name='other-barrier'
					CREATE (b4:DatasetOntology:Object:Mapillary) SET b4.name='guard-rail'
					CREATE (c2:DatasetOntology:Object:Mapillary) SET c2.name='structure'
					CREATE (s:DatasetOntology:Object:Mapillary) SET s.name='building'
					CREATE (s1:DatasetOntology:Object:Mapillary) SET s1.name='bridge'
					CREATE (s2:DatasetOntology:Object:Mapillary) SET s2.name='tunnel'
					CREATE (d:DatasetOntology:Object:Mapillary) SET d.name='person'
					CREATE (d1:DatasetOntology:Object:Mapillary) SET d1.name='rider'
					CREATE (f:DatasetOntology:Object:Mapillary) SET f.name='motorcyclist'
					CREATE (f1:DatasetOntology:Object:Mapillary) SET f1.name='bicyclist'
					CREATE (f2:DatasetOntology:Object:Mapillary) SET f2.name='other-rider'
					CREATE (g:DatasetOntology:Object:Mapillary) SET g.name='general'
					CREATE (g1:DatasetOntology:Object:Mapillary) SET g1.name='discrete'
					CREATE (h:DatasetOntology:Object:Mapillary) SET h.name='crosswalk-zebra'
					CREATE (j:DatasetOntology:Object:Mapillary) SET j.name='sky'
					CREATE (j1:DatasetOntology:Object:Mapillary) SET j1.name='vegetation'
					CREATE (j2:DatasetOntology:Object:Mapillary) SET j2.name='terrain'
					CREATE (j3:DatasetOntology:Object:Mapillary) SET j3.name='mountain'
					CREATE (j4:DatasetOntology:Object:Mapillary) SET j4.name='snow'
					CREATE (j5:DatasetOntology:Object:Mapillary) SET j5.name='water'
					CREATE (j6:DatasetOntology:Object:Mapillary) SET j6.name='sand'
					CREATE (k:DatasetOntology:Object:Mapillary) SET k.name='unlabeled'
					CREATE (k1:DatasetOntology:Object:Mapillary) SET k1.name='ego-vehicle'
					CREATE (k2:DatasetOntology:Object:Mapillary) SET k2.name='car-mount'
					CREATE (l:DatasetOntology:Object:Mapillary) SET l.name='bird'
					CREATE (l1:DatasetOntology:Object:Mapillary) SET l1.name='ground-animal'
					MERGE (w)<-[:subClassOf]-(m)
					MERGE (w)<-[:subClassOf]-(m1)
					MERGE (w)<-[:subClassOf]-(m2)
					MERGE (w)<-[:subClassOf]-(m3)
					MERGE (w)<-[:subClassOf]-(m4)
					MERGE (w)<-[:subClassOf]-(m5)
					MERGE (w)<-[:subClassOf]-(m6)
					MERGE (m)<-[:subClassOf]-(n)
					MERGE (n)<-[:subClassOf]-(q)
					MERGE (n)<-[:subClassOf]-(q1)
					MERGE (n)<-[:subClassOf]-(q2)
					MERGE (m)<-[:subClassOf]-(n1)
					MERGE (m)<-[:subClassOf]-(n2)
					MERGE (m)<-[:subClassOf]-(n3)
					MERGE (m)<-[:subClassOf]-(n4)
					MERGE (m)<-[:subClassOf]-(n5)
					MERGE (m)<-[:subClassOf]-(n6)
					MERGE (m)<-[:subClassOf]-(n7)
					MERGE (m)<-[:subClassOf]-(n8)
					MERGE (m)<-[:subClassOf]-(n9)
					MERGE (m)<-[:subClassOf]-(n10)
					MERGE (m)<-[:subClassOf]-(n11)
					MERGE (m)<-[:subClassOf]-(n12)
					MERGE (m)<-[:subClassOf]-(n13)
					MERGE (m)<-[:subClassOf]-(n14)
					MERGE (m)<-[:subClassOf]-(n15)
					MERGE (m)<-[:subClassOf]-(n16)
					MERGE (n16)<-[:subClassOf]-(z)
					MERGE (n16)<-[:subClassOf]-(z1)
					MERGE (n16)<-[:subClassOf]-(z2)
					MERGE (n16)<-[:subClassOf]-(z3)
					MERGE (n16)<-[:subClassOf]-(z4)
					MERGE (n16)<-[:subClassOf]-(z5)
					MERGE (n16)<-[:subClassOf]-(z6)
					MERGE (n16)<-[:subClassOf]-(z7)
					MERGE (n16)<-[:subClassOf]-(z8)
					MERGE (n16)<-[:subClassOf]-(z9)
					MERGE (n16)<-[:subClassOf]-(z10)
					MERGE (m)<-[:subClassOf]-(n17)
					MERGE (n17)<-[:subClassOf]-(x)
					MERGE (n17)<-[:subClassOf]-(x1)
					MERGE (m1)<-[:subClassOf]-(c)
					MERGE (c)<-[:subClassOf]-(v)
					MERGE (c)<-[:subClassOf]-(v1)
					MERGE (c)<-[:subClassOf]-(v2)
					MERGE (c)<-[:subClassOf]-(v3)
					MERGE (c)<-[:subClassOf]-(v4)
					MERGE (c)<-[:subClassOf]-(v5)
					MERGE (c)<-[:subClassOf]-(v6)
					MERGE (c)<-[:subClassOf]-(v7)
					MERGE (c)<-[:subClassOf]-(v8)
					MERGE (m1)<-[:subClassOf]-(c1)
					MERGE (c1)<-[:subClassOf]-(b)
					MERGE (c1)<-[:subClassOf]-(b1)
					MERGE (c1)<-[:subClassOf]-(b2)
					MERGE (c1)<-[:subClassOf]-(b3)
					MERGE (c1)<-[:subClassOf]-(b4)
					MERGE (m1)<-[:subClassOf]-(c2)
					MERGE (c2)<-[:subClassOf]-(s)
					MERGE (c2)<-[:subClassOf]-(s1)
					MERGE (c2)<-[:subClassOf]-(s2)
					MERGE (m2)<-[:subClassOf]-(d)
					MERGE (m2)<-[:subClassOf]-(d1)
					MERGE (d1)<-[:subClassOf]-(f)
					MERGE (d1)<-[:subClassOf]-(f1)
					MERGE (d1)<-[:subClassOf]-(f2)
					MERGE (m3)<-[:subClassOf]-(g)
					MERGE (m3)<-[:subClassOf]-(g1)
					MERGE (g1)<-[:subClassOf]-(h)
					MERGE (m4)<-[:subClassOf]-(j)
					MERGE (m4)<-[:subClassOf]-(j1)
					MERGE (m4)<-[:subClassOf]-(j2)
					MERGE (m4)<-[:subClassOf]-(j3)
					MERGE (m4)<-[:subClassOf]-(j4)
					MERGE (m4)<-[:subClassOf]-(j5)
					MERGE (m4)<-[:subClassOf]-(j6)
					MERGE (m5)<-[:subClassOf]-(k)
					MERGE (m5)<-[:subClassOf]-(k1)
					MERGE (m5)<-[:subClassOf]-(k2)
					MERGE (m6)<-[:subClassOf]-(l)
					MERGE (m6)<-[:subClassOf]-(l1) """)