import subprocess
import shutil

src_dir = "src"
dest_dir = "build"

proto_file = "vcd_proto-v4.proto"

subprocess.run(["protoc", f"--proto_path={src_dir}", f"--python_out={dest_dir}", proto_file])
out_file = dest_dir + "/vcd_proto_v4_pb2.py"
shutil.move(out_file, "../vcd/proto.py")