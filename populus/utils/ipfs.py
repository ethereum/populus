import operator
import hashlib

from eth_utils import (
    to_dict,
    compose,
)

from populus.pb.ipfs_file_pb2 import (
    Data,
    PBNode,
)

from .six import (
    parse,
)
from .base58 import (
    b58encode,
)


def create_ipfs_uri(ipfs_hash):
    return "ipfs://{0}".format(ipfs_hash)


def is_ipfs_uri(value):
    parse_result = parse.urlparse(value)
    if parse_result.scheme != 'ipfs':
        return False
    if not parse_result.netloc and not parse_result.path:
        return False

    return True


def extract_ipfs_path_from_uri(value):
    parse_result = parse.urlparse(value)

    if parse_result.netloc:
        if parse_result.path:
            return ''.join((parse_result.netloc, parse_result.path))
        else:
            return parse_result.netloc
    else:
        return parse_result.path.lstrip('/')


def resolve_ipfs_path_to_hash(ipfs_client, ipfs_path):
    result = ipfs_client.resolve(ipfs_path)
    resolved_path = result['Path']
    _, _, ipfs_hash = resolved_path.rpartition('/')
    return ipfs_hash


def get_ipfs_object_type(ipfs_client, ipfs_path):
    object_metadata = ipfs_client.file_ls(ipfs_path)

    if not object_metadata:
        return False

    resolved_hash = object_metadata['Arguments'][ipfs_path]

    type_getter = compose(
        operator.itemgetter('Objects'),
        operator.itemgetter(resolved_hash),
        operator.itemgetter('Type'),
    )

    return type_getter(object_metadata)


def is_directory(ipfs_client, ipfs_path):
    return get_ipfs_object_type(ipfs_client, ipfs_path) == 'Directory'


def is_file(ipfs_client, ipfs_path):
    return get_ipfs_object_type(ipfs_client, ipfs_path) == 'File'


@to_dict
def walk_ipfs_tree(ipfs_client, ipfs_path, prefix='./'):
    """
    Given an IPFS hash or path, this walks down the filesystem tree and returns
    a generator of 2-tuples where the first item is the filesystem path and the
    second value is the ipfs hash of the file that belongs at that hash
    """
    ipfs_hash = resolve_ipfs_path_to_hash(ipfs_client, ipfs_path)

    if is_file(ipfs_client, ipfs_hash):
        yield (prefix, ipfs_hash)
    elif is_directory(ipfs_client, ipfs_hash):
        links = ipfs_client.file_ls(ipfs_hash)['Objects'][ipfs_hash]['Links']

        for link in links:
            link_hash = link['Hash']
            link_name = link['Name']

            if is_file(ipfs_client, link_hash):
                sub_prefix = '{prefix}{name}'.format(prefix=prefix, name=link_name)
                yield (sub_prefix, link_hash)
            elif is_directory(ipfs_client, link_hash):
                sub_prefix = '{prefix}{name}/'.format(prefix=prefix, name=link_name)
                for value in walk_ipfs_tree(ipfs_client, link_hash, sub_prefix):
                    yield value
    else:
        raise ValueError("Unsupported type.  Must be an IPFS file or directory")


SHA2_256 = b'\x12'
LENGTH_32 = b'\x20'


def multihash(value):
    data_hash = hashlib.sha256(value).digest()

    multihash_bytes = SHA2_256 + LENGTH_32 + data_hash
    return multihash_bytes


def serialize_file(file_path):
    file_data = open(file_path, 'rb').read()
    file_size = len(file_data)

    data_protobuf = Data(
        Type=Data.DataType.Value('File'),
        Data=file_data,
        filesize=file_size,
    )
    data_protobuf_bytes = data_protobuf.SerializeToString()

    file_protobuf = PBNode(Links=[], Data=data_protobuf_bytes)

    return file_protobuf


def generate_file_hash(file_path):
    file_protobuf = serialize_file(file_path)
    file_protobuf_bytes = file_protobuf.SerializeToString()
    file_multihash = multihash(file_protobuf_bytes)
    return b58encode(file_multihash)
