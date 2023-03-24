from chainingiterator import Chi
import pytest
import copy
from typing import Generator, Any


def test_construct_next():
    base = {1: 1, 2: 2, 3: 3}
    chi = Chi(base.items())

    for i in range(1, 4):
        assert chi.next() == (i, i)

    with pytest.raises(StopIteration):
        chi.next()
        chi.collect(list)
