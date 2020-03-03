import sys
sys.path.insert(0, '.')
from build.vcd_proto_v4_pb2 import VCD
from google.protobuf.json_format import MessageToJson


def proto_bin2json(proto_path, json_path):
    vcd_message = VCD()

    with open(proto_path, "rb") as f:
        vcd_message.ParseFromString(f.read())

    with open(json_path, "w") as f:
        f.write(MessageToJson(vcd_message, preserving_proto_field_name=True,
                              indent=0))


if __name__ == "__main__":
    proto_file = "vcd_proto_test.txt"
    json_file = "json_files/vcd_json_test.json"

    proto_bin2json(proto_file, json_file)
