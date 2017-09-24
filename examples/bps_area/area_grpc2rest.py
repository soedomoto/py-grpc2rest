# import pkg_resources
# from grpc_tools import protoc
#
# # Compile proto file
# # proto_include = pkg_resources.resource_filename('grpc_tools', '_proto')
# # protoc.main(['--proto_path={}'.format(proto_include), '--proto_path=.', '--python_out=.', 'hello.proto'])

import os
import sys

CD = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(CD, os.pardir, os.pardir))

from grpc2rest.server import Server

try:
    app = Server()
    app.register_proto(os.path.join(CD, 'area_pb2.py'), os.path.join(CD, 'area_client.py'))
    print('running server on 0.0.0.0:8888')
    app.run(debug=True)
except KeyboardInterrupt:
    pass