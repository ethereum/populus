from populus.utils.functional import (
    star_apply,
)


def test_star_apply():
    def fn(*args):
        return args

    assert fn(['a', 'b']) == (['a', 'b'],)
    assert star_apply(fn)(['a', 'b']) == ('a', 'b')
