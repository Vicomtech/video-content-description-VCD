import json
import os
import time
import sys
sys.path.insert(0, "..")
import vcd.core as core
import vcd.types as types

from pycallgraph2 import PyCallGraph
from pycallgraph2.output import GraphvizOutput
#from pycallgraph2 import Config

def vcd_add_object_debug():
    time_0 = time.time()
    vcd = core.VCD()
    for frame_num in range(0, 10000):
        if frame_num % 10 == 0:
            uid = vcd.add_object('CARLOTA' + str(frame_num), '#Car', frame_value=frame_num)
        vcd.add_object_data(uid, types.bbox("shape", (0, 0, 100, 200)), frame_value=frame_num)
        
    time_1 = time.time()
    elapsed_time_loop = time_1 - time_0
    print("Loop {} seconds".format(elapsed_time_loop))
    vcd.save(file_name='./png/vcd_add_object_debug_10000.json')
    #print("Loop: %s seconds. " % elapsed_time_loop)

    # time_0 = time.time()
    # vcd.save('./json/vcd_add_object_debug.json', pretty=False)
    # time_1 = time.time()
    # elapsed_time_loop = time_1 - time_0
    # print("Save: %s seconds. " % elapsed_time_loop)

############################
## CREATE CONTENT
############################
print_graph = True # Needs to be set to False to enable debugging
if print_graph:
    with PyCallGraph(output=GraphvizOutput(output_file='./png/vcd_add_object_debug_10000.png', font_size=8)):
        print("Running " + os.path.basename(__file__))
        vcd_add_object_debug()
else:
    print("Running " + os.path.basename(__file__))
    vcd_add_object_debug()

#if __name__=="__main__":
#    print("Running " + os.path.basename(__file__))
#    vcd_add_object_debug()
