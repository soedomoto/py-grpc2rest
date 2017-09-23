import imp
import importlib
import json
import sys
from google.protobuf import descriptor_pb2, json_format
from grpc2rest.exceptions import ProtoParseException


def search_method_option_in_service(stubs, service, call):
    idt = get_service_identify(stubs, service)
    if not idt:
        raise ProtoParseException('not registed service')
    options = dict()

    for k, v in idt.items():
        if str(k) == call:
            options = v
            break

    if options:
        return options
    raise ProtoParseException('no such a call')


def get_service_identify(stubs, service_name):
    stub = stubs.get(service_name)
    if stub:
        if stub.server_pb2_import_type == 'path':
            if stub.server_pb2_module_name in sys.modules.keys():
                md = importlib.import_module(stub.server_pb2_module_name)
            else:
                md = imp.load_source(
                    stub.server_pb2_module_name,
                    stub.server_pb2_module_path)
        else:
            md = importlib.import_module(stub.server_pb2_module)
        return get_service_identify_from_pb_file(md)


def get_service_identify_from_pb_file(pb2):
    method_mapping = dict()
    p = descriptor_pb2.FileDescriptorProto()
    pb2.DESCRIPTOR.CopyToProto(p)
    for s in p.service:
        for m in s.method:
            if not method_mapping.get(m.name):
                method_mapping[m.name] = dict()

            for e, v in m.options._extensions_by_name.items():
                a = e

            http_method = m.options.Extensions[pb2.http_method]
            md = http_method.DESCRIPTOR.fields_by_name['name']

            desc = m.DESCRIPTOR
            for k, v in desc.fields_by_name.items():
                o = v.GetOptions()
                f = v.ListFields()

                # os = o.Extensions[http_method]

            #     oDesc = o.DESCRIPTOR
            #     for i, j in oDesc.extensions_by_name.items():
            #         method_mapping[m.name][i] = j

                # if hasattr(v, '_fields'):
                #     for i, j in v._fields.items():
                #         method_mapping[m.name][i.name] = j
    return method_mapping


def dynamic_client_getter(stubs, service_name):
    stub = stubs.get(service_name)
    if stub:
        if stub.client_import_type == 'path':
            if stub.client_module_name in sys.modules.keys():
                md = importlib.import_module(stub.client_module_name)
            else:
                md = imp.load_source(
                    stub.client_module_name,
                    stub.client_module_path)
        else:
            md = importlib.import_module(stub.client_module)
        cl = getattr(md, stub.get_client_func)
        return cl()


def pb2json(pb):
    return json.loads(json_format.MessageToJson(pb, including_default_value_fields=True))


def json2pb(pb, js):
    if isinstance(js, dict):
        js = json.dumps(js)
    return json_format.Parse(js, pb)
