import atexit
from examples.simple import hello_pb2
from grpc2rest.client import Client


class ClientImpl(Client):
    def __init__(self, host='0.0.0.0', port=50051, size=1):
        Client.__init__(self, host, port, size, hello_pb2.beta_create_SimpleService_stub)

    def Hello(self, say, with_call=False):
        request = hello_pb2.HelloRequest(say=say)
        return self.stub.Hello(request, 3, with_call=with_call)


def get_client():
    if ClientImpl.get_cache():
        return ClientImpl.get_cache()
    return ClientImpl()


def exit_handler():
    if ClientImpl.get_cache():
        ClientImpl.get_cache().shutdown()

atexit.register(exit_handler)
