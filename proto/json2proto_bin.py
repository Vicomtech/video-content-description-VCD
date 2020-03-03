import sys
import time
sys.path.insert(0, '.')
from build.vcd_proto_v4_pb2 import VCD
from google.protobuf.json_format import Parse


def json2proto_bin(json_path, proto_path):
    vcd_message = VCD()
    with open(json_path, "r") as f:
        start_time = time.time()
        Parse(f.read(), vcd_message)
        print(f"Parse time: {time.time()-start_time}")

    with open(proto_path, "wb") as f:
        start_time = time.time()
        f.write(vcd_message.SerializeToString())
        print(f"Serialize time: {time.time()-start_time}")


if __name__ == "__main__":

    proto_file = "proto_files/vcd_proto_test.txt"
    json_file = "../tests/etc/test_timestamp_metadata.json"

    json2proto_bin(json_file, proto_file)
