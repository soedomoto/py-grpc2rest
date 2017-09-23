# import pkg_resources
# from grpc_tools import protoc
#
# # Compile proto file
# # proto_include = pkg_resources.resource_filename('grpc_tools', '_proto')
# # protoc.main(['--proto_path={}'.format(proto_include), '--proto_path=.', '--python_out=.', 'hello.proto'])
import os, sys

CD = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(CD, os.pardir, os.pardir))

from grpc2rest.server import Stub, Server

stub = Stub()
stub.name = 'SimpleService'
stub.client_import_type = 'path'
stub.client_module_path = os.path.join(CD, 'hello_client.py')
stub.client_module_name = 'hello_client'
stub.get_client_func = 'get_client'

stub.server_pb2_import_type = 'path'
stub.server_pb2_module_path = os.path.join(CD, 'hello_pb2.py')
stub.server_pb2_module_name = 'hello_pb2'

try:
    app = Server()
    app.register(stub)
    print('running server on 0.0.0.0:8888')
    app.run(debug=True)
except KeyboardInterrupt:
    pass
