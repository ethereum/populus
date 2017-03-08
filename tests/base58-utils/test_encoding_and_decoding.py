from hypothesis import (
    given,
    strategies as st,
)

from populus.utils.base58 import (
    b58encode,
    b58decode,
)


@given(value=st.binary(max_size=256))
def test_round_trip(value):
    encoded_value = b58encode(value)
    decoded_value = b58decode(encoded_value)
    assert decoded_value == value
