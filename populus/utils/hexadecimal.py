from hexbytes import HexBytes


def hexbytes_to_hexstr(val):
    if isinstance(val, HexBytes):
        return val.hex()
    else:
        return val
