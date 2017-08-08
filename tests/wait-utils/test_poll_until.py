import itertools

import pytest

from populus.utils.compat import (
    Timeout,
)
from populus.utils.wait import (
    poll_until,
)


def test_poll_until_returns_when_success():
    counter = itertools.count()
    poll_fn = lambda: next(counter)  # noqa: E731
    success_fn = lambda v: v == 3  # noqa: E731

    value = poll_until(poll_fn, success_fn, 1, lambda: 0)
    assert value == 3
    assert next(counter) == 4


def test_poll_until_times_out_if_no_success():
    counter = itertools.count()
    poll_fn = lambda: next(counter)  # noqa: E731
    success_fn = lambda v: False  # noqa: E731

    with pytest.raises(Timeout):
        poll_until(poll_fn, success_fn, 0.0001, lambda: 0)
    assert next(counter) > 0
