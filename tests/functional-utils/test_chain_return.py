from populus.utils.functional import (
    chain_return,
)


def test_chain_return():
    @chain_return
    def doit():
        for i in range(5):
            yield range(i)

    actual = tuple(doit())
    expected = (0, 0, 1, 0, 1, 2, 0, 1, 2, 3)
    assert actual == expected


def test_chain_return_with_empty_return():
    @chain_return
    def doit():
        if False:
            yield [1, 3, 3]

    actual = tuple(doit())
    expected = tuple()
    assert actual == expected
