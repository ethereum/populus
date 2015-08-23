import os
from populus.serpent import (
    serpent,
    get_signature,
)


TEST_DIR = os.path.dirname(__file__)

source_file = os.path.join(TEST_DIR, 'projects', 'test-01', 'contracts', 'mul2.se')
source_dir = os.path.dirname(source_file)
source_code = """
def double(x):
    return (x * 2)
"""
raw_code = '604380600b600039604e567c010000000000000000000000000000000000000000000000000000000060003504636ffa1caa81141560415760043560405260026040510260605260206060f35b505b6000f3'


def test_compile_from_file():
    code = serpent(input_file=source_file, raw=True)
    assert code == raw_code


def test_compile_from_source():
    code = serpent(source=source_code, raw=True)
    assert code == raw_code
