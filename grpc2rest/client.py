from random import randint

import grpc
from grpc._cython.cygrpc import ConnectivityState
from grpc.beta import implementations


class ChannelPool(object):
    service_stub_fn = None

    def __init__(self, host, port, pool_size=10, service_stub_fn=None):
        self.host = host
        self.port = port
        self.pool_size = pool_size
        self.service_stub_fn = service_stub_fn
        self.channels = []
        self.stubs = []
        # only index, no ref!
        # and this is a stub rank!
        self.working_channel_indexs = set()
        self.connect()

    def connect(self):
        for i in range(self.pool_size):
            channel = grpc.insecure_channel('{}:{}'.format(self.host, self.port))
            stub = self.service_stub_fn(channel)
            # we need to make channels[i] == stubs[i]->channel
            self.channels.append(channel)
            self.stubs.append(stub)

    def shutdown(self):
        for channel in self.channels:
            del channel
        del self.channels
        for stub in self.stubs:
            del stub
        del self.stubs
        self.channels = []
        self.stubs = []

    def get_stub(self):
        index = randint(0, self.pool_size - 1)
        self.working_channel_indexs.add(index)
        return self.stubs[index]

    def __del__(self):
        self.shutdown()


class Client(object):
    def __init__(self, host='0.0.0.0', port=50051, pool_size=10, service_stub_fn=None):
        self.pool = ChannelPool(host, port, pool_size, service_stub_fn)
        self.pool.connect()
        self.update_cache()

    def update_cache(self):
        raise Exception('Not Implemented')

    @classmethod
    def get_cache(cls):
        raise Exception('Not Implemented')

    def shutdown(self):
        self.pool.shutdown()

    @property
    def stub(self):
        return self.pool.get_stub()