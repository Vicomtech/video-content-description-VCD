# Building the VCD protobuff

The VCD schema is manually written as a .proto file trying to mimic the 
structure of VCD as defined in the JSON schema.
This file can be found at: 

````
\proto\src\vcd_proto-v4.proto
````

Once ready, we need to build it to produce the classes file, in our case, for
 Python language: 

````
\proto\build\vcd_proto_v4_pb2.py
````

To build **vcd_proto_v4_pb2.py** we need to install the Protocol buffers compiler
and execute the following command:

````
protoc --proto_path=vcd_proto-v4.proto --python_out=vcd_proto_v4_pb2.py
````

The script **python_object_from_proto.py** can be used to launch the build.

Finally, the scripts in **json2proto_bin.py** and **proto_bin2json.py** 
can be safely used to convert JSON-proto and viceversa. Some examples of conversion
can be found at:

````
\tests\test_serializer.py
````