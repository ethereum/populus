"""
Lifted from the base58 package.
"""
import sys


# 58 character alphabet used
ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


if sys.version_info.major == 2:
    iseq = lambda s: map(ord, s)  # noqa: E731
    bseq = lambda s: ''.join(map(chr, s))  # noqa: E731
    buffer = lambda s: s  # noqa: E731
else:
    iseq = lambda s: s  # noqa: E731
    bseq = bytes  # noqa: E731
    buffer = lambda s: s.buffer  # noqa: E731


def b58encode(v):
    origlen = len(v)
    v = v.lstrip(b'\0')
    newlen = len(v)

    p, acc = 1, 0
    for c in iseq(v[::-1]):
        acc += p * c
        p = p << 8

    result = ''
    while acc > 0:
        acc, mod = divmod(acc, 58)
        result += ALPHABET[mod]

    return (result + ALPHABET[0] * (origlen - newlen))[::-1]


def b58decode(v):
    if not isinstance(v, str):
        v = v.decode('ascii')

    origlen = len(v)
    v = v.lstrip(ALPHABET[0])
    newlen = len(v)

    p, acc = 1, 0
    for c in v[::-1]:
        acc += p * ALPHABET.index(c)
        p *= 58

    result = []
    while acc > 0:
        acc, mod = divmod(acc, 256)
        result.append(mod)

    return (bseq(result) + b'\0' * (origlen - newlen))[::-1]
