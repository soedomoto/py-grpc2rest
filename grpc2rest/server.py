import imp
import importlib
import sys
import tornado.ioloop
import tornado.web
from grpc2rest.handler import ServiceHandler, IndexHandler
from grpc2rest.utils import list_services_from_pb_file


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
        if self.server_pb2_import_type == 'path':
            if self.server_pb2_module_name in sys.modules.keys():
                md = importlib.import_module(self.server_pb2_module_name)
            else:
                md = imp.load_source(
                    self.server_pb2_module_name,
                    self.server_pb2_module_path)
        else:
            md = importlib.import_module(self.server_pb2_module)
        return list_services_from_pb_file(md)


class Server(object):
    stubs = dict()

    def __init__(self, host='0.0.0.0', port=8888, debug=False):
        self.host = host
        self.port = port
        self.debug = debug

    def __repr__(self):
        return 'gRPC2REST Server'

    def register(self, stub):
        stub.set_server(self)
        self.stubs[stub.name] = stub

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