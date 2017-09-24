import atexit

from google.protobuf.empty_pb2 import Empty

from examples.bps_area import area_pb2
from grpc2rest.client import Client


class ProvinceImpl(Client):
    client_cache = None

    def __init__(self, host='0.0.0.0', port=50051, size=1):
        Client.__init__(self, host, port, size, area_pb2.ProvinceServiceStub)

    def update_cache(self):
        ProvinceImpl.client_cache = self

    @classmethod
    def get_cache(cls):
        return ProvinceImpl.client_cache

    def list(self, with_call=False):
        return self.stub.list(Empty(), 3)

    def add(self, id=None, code=None, name=None, lastId=None, with_call=False):
        return self.stub.add(area_pb2.Province(code=code, name=name), 3)


class RegencyImpl(Client):
    client_cache = None

    def __init__(self, host='0.0.0.0', port=50051, size=1):
        Client.__init__(self, host, port, size, area_pb2.RegencyServiceStub)

    def update_cache(self):
        RegencyImpl.client_cache = self

    @classmethod
    def get_cache(cls):
        return RegencyImpl.client_cache

    def list(self, with_call=False):
        return self.stub.list(Empty(), 3)


def get_client_province_service():
    if ProvinceImpl.get_cache():
        return ProvinceImpl.get_cache()
    return ProvinceImpl(port=5052)


def get_client_regency_service():
    if RegencyImpl.get_cache():
        return RegencyImpl.get_cache()
    return RegencyImpl(port=5052)


def exit_handler():
    if ProvinceImpl.get_cache():
        ProvinceImpl.get_cache().shutdown()
    if RegencyImpl.get_cache():
        RegencyImpl.get_cache().shutdown()

atexit.register(exit_handler)
