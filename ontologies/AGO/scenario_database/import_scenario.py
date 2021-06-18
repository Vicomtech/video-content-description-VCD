import os, sys
from def_import_VCDscenario_to_Neo4j import Neo4jScenarioDB

# Import VCD:
sys.path.insert(0, "../video-content-description-VCD")
from vcd import core

# Create VCD object:
vcd = core.VCD()
ont_uid_0 = vcd.add_ontology("http://vcd.vicomtech.org/ontology/automotive")


def test_import_scenario_from_file():
    # Loop over KITTI VCD JSON files
    path = "../AGO/scenario_database/VCD_files/KITTI"
    vcd_file_names = os.listdir(path)
    for vcd_file_name in vcd_file_names:
        name_scene = os.path.splitext(os.path.basename(vcd_file_name))[0]
        vcd = core.VCD(path+'/'+vcd_file_name)
        Neo4jScenarioDB.create_scenario(scenario_uid=name_scene + '_static', vcd=vcd, only_static=True)

    # Loop over ALKS VCD JSON files
    path2 = "../AGO/scenario_database/VCD_files/ALKS"
    vcd_file_names = os.listdir(path2)
    for vcd_file_name in vcd_file_names:
        name_scene = os.path.splitext(os.path.basename(vcd_file_name))[0]
        vcd = core.VCD(path2+'/'+vcd_file_name)
        Neo4jScenarioDB.create_scenario(scenario_uid=name_scene + '_static', vcd=vcd, only_static=True)


test_import_scenario_from_file()