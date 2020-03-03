import os
import sys
sys.path.insert(0, "..")

from json2proto_bin import json2proto_bin

directory_vcd = '../../converters/nuScenesConverter/vcd_files'
directory_proto = os.path.dirname(os.path.abspath(__file__))+'/nuScenesProtoFiles'
print(os.path.abspath(os.path.join(directory_proto, os.pardir)))
for filename in os.listdir(directory_vcd):
    if filename.endswith(".json"):
        json2proto_bin(directory_vcd+"/"+filename, os.path.splitext(directory_proto+"/"+filename)[0]+".txt")
