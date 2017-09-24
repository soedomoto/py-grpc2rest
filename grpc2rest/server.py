import os
from collections import OrderedDict

import tornado.ioloop
import tornado.web
from grpc2rest.handler import ServiceHandler, IndexHandler
from grpc2rest.utils import list_services_from_pb_file, import_module, camel_to_snake_case


class Stub(object):
    server = None

    name = ''
    client_import_type = 'module'
    client_module = ''
    client_module_path = ''
    client_module_name = ''
    get_client_func = 'get_client'

    server_pb2_import_type = 'module'
    server_pb2_module = ''
    server_pb2_module_path = ''
    server_pb2_module_name = ''

    def set_server(self, server):
        self.server = server

    @property
    def endpoints(self):
        md = import_module(self.server_pb2_module_path, self.server_pb2_module_name,
                           self.server_pb2_import_type)
        services = list_services_from_pb_file(md)
        return services[self.name]


class Server(object):
    stubs = OrderedDict()

    def __init__(self, host='0.0.0.0', port=8888, debug=False):
        self.host = host
        self.port = port
        self.debug = debug

    def __repr__(self):
        return 'gRPC2REST Server'

    def register(self, stub):
        stub.set_server(self)
        self.stubs[stub.name] = stub

    def register_proto(self, pb2_file, client_file):
        pb2_mod_name = os.path.splitext(os.path.basename(pb2_file))[0]
        md = import_module(pb2_file, pb2_mod_name, 'path')
        services = list_services_from_pb_file(md)

        for sn, s in services.items():
            stub = Stub()
            stub.name = sn

            client_mod_name = os.path.splitext(os.path.basename(client_file))[0]
            stub.client_import_type = 'path'
            stub.client_module_path = client_file
            stub.client_module_name = client_mod_name
            stub.get_client_func = 'get_client_{}'.format(camel_to_snake_case(sn))

            stub.server_pb2_import_type = 'path'
            stub.server_pb2_module_path = pb2_file
            stub.server_pb2_module_name = pb2_mod_name

            self.register(stub)

    def request_handler(self, request):
        metadata = ()
        return metadata

    def status_handler(self, response):
        return 200

    def run(self, debug=False):
        app = tornado.web.Application([
            ('/service/([^/]+)/([^/]+)', ServiceHandler, dict(debug=debug, server=self)),
            ('/', IndexHandler, dict(debug=debug, server=self))
        ], debug=debug)

        app.listen(self.port)
        tornado.ioloop.IOLoop.current().start()