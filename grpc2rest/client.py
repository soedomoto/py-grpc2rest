from random import randint
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

    def flush_channels(self):
        # call this method to check all the channels status
        # if channel connection is failed or idle
        # we could try to reconnect sometime
        channels = [self.channels[i] for i in self.working_channel_indexs]
        for channel in channels:
            try:
                state = channel._low_channel.check_connectivity_state(True)
                if state == ConnectivityState.CONNECTING:
                    self.on_channel_connection(channel, state)
                elif state == ConnectivityState.TRANSIENT_FAILURE:
                    self.on_transient_failure(channel, state)
                elif state == ConnectivityState.FATAL_FAILURE:
                    self.on_fatal_failure(channel, state)
                else:
                    self.on_success(channel, state)
            except Exception as e:
                self.on_exception(channel, state, e)

    def on_channel_connection(self, channel, state):
        pass

    def on_transient_failure(self, channel, state):
        pass

    def on_fatal_failure(self, channel, state):
        pass

    def on_success(self, channel, state):
        pass

    def on_exception(self, channel, state, e):
        pass

    def connect(self):
        for i in range(self.pool_size):
            channel = implementations.insecure_channel(self.host, self.port)
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


client_cache = None
class Client(object):
    def __init__(self, host='0.0.0.0', port=50051, pool_size=10, service_stub_fn=None):
        self.pool = ChannelPool(host, port, pool_size, service_stub_fn)
        self.pool.connect()
        self.update_cache()

    def update_cache(self):
        global client_cache
        client_cache = self

    @classmethod
    def get_cache(cls):
        global client_cache
        return client_cache

    def shutdown(self):
        self.pool.shutdown()

    @property
    def stub(self):
        return self.pool.get_stub()