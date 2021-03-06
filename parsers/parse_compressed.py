import base64
import re
import zlib


zip_edge = {
    'color': {
        'color': '#2C63FF'
    },
    'title': 'Compression-related Parsing Functions',
    'label': 'zip'
}

b64_zip_edge = {
    'color': {
        'color': '#2C63FF'
    },
    'title': 'Compression-related Parsing Functions',
    'label': 'b64+zip'
}


def run(unfurl, node):

    if not isinstance(node.value, str):
        return False

    if node.data_type == 'zlib':
        inflated_str = zlib.decompress(node.value)
        unfurl.add_to_queue(
            data_type='This data was inflated using zlib', key=None, value=inflated_str, parent_id=node.node_id,
            incoming_edge_config=zip_edge)
        return

    # This checks for base64 encoding, which is often used before compression. Initially, the base64 decoding was
    # in parse_base64.py, but the intermediary node seemed like not useful clutter. I moved it here and combined
    # the parser into b64+zlib
    if len(node.value) % 4 == 1:
        # A valid b64 string will not be this length
        return False

    m = re.match(r'^[A-Za-z0-9_=\-]{16,}$', node.value)
    if m:
        decoded = base64.urlsafe_b64decode(unfurl.add_b64_padding(node.value))
        try:
            inflated_bytes = zlib.decompress(decoded)
        except:
            return

        try:
            inflated_str = inflated_bytes.decode('ascii', errors='strict')
            unfurl.add_to_queue(
                data_type='string', key=None, value=inflated_str, parent_id=node.node_id,
                hover='This data was base64-decoded, then zlib inflated', incoming_edge_config=b64_zip_edge)
            return
        except:
            pass

        unfurl.add_to_queue(
            data_type='string', key=None, value=inflated_bytes, parent_id=node.node_id,
            hover='This data was inflated using zlib', incoming_edge_config=zip_edge)
