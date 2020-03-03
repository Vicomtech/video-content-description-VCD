import subprocess

src_dir = "src"
dest_dir = "build"

proto_file = "vcd_proto-v4.proto"

subprocess.run(["protoc", f"--proto_path={src_dir}", f"--python_out={dest_dir}", proto_file])