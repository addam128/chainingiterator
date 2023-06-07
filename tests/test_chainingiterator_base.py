from chainingiterator import Chi
import pytest
import copy
from typing import Generator, Any, Tuple


def test_construct_next():
    base = [1, 2, 3]
    chi = Chi(base)

    for i in base:
        assert chi.next() == i

    with pytest.raises(StopIteration):
        chi.next()
        chi.collect(list)


def test_map():
    base = [1, 2, 3]
    chi = Chi(base).map(lambda n: n + 1)
    assert base == [1, 2, 3]
    builtin = map(lambda n: n + 1, base)
    assert base == [1, 2, 3]

    for _ in range(3):
        assert chi.next() == next(builtin)

    with pytest.raises(StopIteration):
        chi.next()

    assert base == [1, 2, 3]


def test_collect():
    base = [1, 2, 3]
    chi = Chi(base).map(lambda n: n + 1)
    assert base == [1, 2, 3]
    builtin = map(lambda n: n + 1, base)
    assert base == [1, 2, 3]

    assert list(builtin) == chi.collect(list)

    with pytest.raises(StopIteration):
        chi.collect(list)


def test_builtin_for():
    base = [1, 2, 3]
    chi = Chi(base)
    start = 1
    for i in chi:
        assert i == start
        start += 1


def test_filter():
    base = [1, 2, 3, 4, 5, 6]
    result = {1, 3, 5}

    chi = Chi(base).filter(lambda n: n % 2 != 0)

    assert result == chi.collect(set)

    assert base == [1, 2, 3, 4, 5, 6]


def test_filter_map():
    base = [1, 2, 3, 4, 5, 6]
    result = {7, 9, 11}

    chi = Chi(base).filter(lambda n: n % 2 != 0).map(lambda n: n + 6)

    assert result == chi.collect(set)

    assert base == [1, 2, 3, 4, 5, 6]


def test_zip_foreach():
    base = [1, 2, 3, 4, 5, 6]
    result = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)]
    placeholder = []

    Chi(base).zip(base).foreach(lambda p: placeholder.append(p))
    assert placeholder == result

    assert base == [1, 2, 3, 4, 5, 6]


def test_all():
    base = [1, 2, 3, 4, 5, 6]

    assert Chi(base).all(lambda num: num < 7) is True
    assert Chi(base).all(lambda num: num < 6) is False

    with pytest.raises(StopIteration):
        chi = Chi(base)
        assert chi.all(lambda num: num < 7) is True
        chi.collect(set)

    assert base == [1, 2, 3, 4, 5, 6]


def test_any():
    base = [1, 2, 3, 4, 5, 6]

    assert Chi(base).any(lambda num: num == 3) is True
    assert Chi(base).any(lambda num: num == 9) is False

    with pytest.raises(StopIteration):
        chi = Chi(base)
        assert chi.any(lambda num: num < 7) is True
        chi.collect(set)

    assert base == [1, 2, 3, 4, 5, 6]


def test_next_chunk():
    base = [1, 2, 3, 4, 5, 6]
    chi = Chi(base)

    assert chi.next_chunk(4) == [1, 2, 3, 4]
    assert chi.next_chunk(4) == [5, 6]

    with pytest.raises(StopIteration):
        chi.collect(list)

    assert base == [1, 2, 3, 4, 5, 6]


def test_enumerate():
    base = [1, 2, 3, 4, 5, 6]
    chi = Chi(base).enumerate()

    for idx, num in chi:
        assert num == base[idx]

    assert base == [1, 2, 3, 4, 5, 6]


def test_nth():
    base = [1, 2, 3, 4, 5, 6]

    assert Chi(base).nth(0) == 1
    assert Chi(base).nth(1) == 2
    assert Chi(base).nth(2) == 3
    assert Chi(base).nth(3) == 4
    assert Chi(base).nth(4) == 5
    assert Chi(base).nth(5) == 6

    with pytest.raises(IndexError):
        Chi(base).nth(6)

    with pytest.raises(StopIteration):
        chi = Chi(base)
        assert chi.nth(1) == 2
        chi.collect(list)

    assert base == [1, 2, 3, 4, 5, 6]


def test_count():
    base = [1, 2, 3, 4, 5, 6]

    chi = Chi(base)
    assert chi.count() == 6

    with pytest.raises(StopIteration):
        chi.collect(set)
    assert base == [1, 2, 3, 4, 5, 6]


def test_chain():
    base = [1, 2, 3, 4, 5, 6]
    extension = [7, 8, 9]

    chi = Chi(base).chain(extension)
    res = copy.copy(base)
    res.extend(extension)
    assert chi.collect(list) == res
    assert base == [1, 2, 3, 4, 5, 6]


def test_take_while():
    base = [1, 2, 3, 4, 5, 6]

    assert Chi(base).take_while(lambda n: n < 5).collect(list) == [1, 2, 3, 4]
    assert base == [1, 2, 3, 4, 5, 6]


def test_skip_while():
    base = [1, 2, 3, 4, 5, 6]

    assert Chi(base).skip_while(lambda n: n < 4).collect(list) == [5, 6]
    assert base == [1, 2, 3, 4, 5, 6]


def test_discard():
    base = [1, 2, 3, 4, 5, 6]
    chi = Chi(base).discard()

    with pytest.raises(StopIteration):
        chi.next()

    assert base == [1, 2, 3, 4, 5, 6]


def test_find_first():
    base = [1, 2, 3, 4, 5, 6]
    chi = Chi(base)
    assert chi.find_first(lambda a: a // 2 == 2) == 4

    with pytest.raises(StopIteration):
        chi.next()

    assert base == [1, 2, 3, 4, 5, 6]


def test_index():
    base = [1, 2, 3, 4, 5, 6]
    chi = Chi(base)
    assert chi.index(lambda a: a // 2 == 2) == 3

    with pytest.raises(StopIteration):
        chi.next()

    assert base == [1, 2, 3, 4, 5, 6]


def test_take():
    base = [1, 2, 3, 4, 5, 6]
    chi = Chi(base)
    assert chi.take(3).collect(list) == [1, 2, 3]

    with pytest.raises(StopIteration):
        chi.next()

    assert base == [1, 2, 3, 4, 5, 6]


def test_step_by():
    base = [1, 2, 3, 4, 5, 6]

    assert Chi(base).step_by(1).collect(list) == base
    assert Chi(base).step_by(2).collect(list) == [1, 3, 5]
    assert Chi(base).step_by(3).collect(list) == [1, 4]
    assert Chi(base).step_by(4).collect(list) == [1, 5]
    assert Chi(base).step_by(5).collect(list) == [1, 6]
    assert Chi(base).step_by(6).collect(list) == [1]

    assert base == [1, 2, 3, 4, 5, 6]


def test_skip():
    base = [1, 2, 3, 4, 5, 6]

    assert Chi(base).skip(0).collect(list) == [1, 2, 3, 4, 5, 6]
    assert Chi(base).skip(1).collect(list) == [2, 3, 4, 5, 6]
    assert Chi(base).skip(2).collect(list) == [3, 4, 5, 6]
    assert Chi(base).skip(3).collect(list) == [4, 5, 6]
    assert Chi(base).skip(4).collect(list) == [5, 6]
    assert Chi(base).skip(5).collect(list) == [6]
    assert Chi(base).skip(6).collect(list) == []

    assert base == [1, 2, 3, 4, 5, 6]


def test_intersperse():
    base = [1, 2, 3, 4, 5, 6]

    assert Chi(base).intersperse("f").collect(list) == [
        1,
        "f",
        2,
        "f",
        3,
        "f",
        4,
        "f",
        5,
        "f",
        6,
        "f",
    ]
    assert base == [1, 2, 3, 4, 5, 6]


def test_last():
    base = [1, 2, 3, 4, 5, 6]

    assert Chi(base).last() == 6
    assert base == [1, 2, 3, 4, 5, 6]


def test_foldl_sum():
    base = [1, 2, 3, 4, 5, 6]

    assert Chi(base).foldl(accumulator=0, func=lambda acc, n: acc + n) == sum(base)
    chi = Chi(base)
    assert chi.foldl(accumulator=0, func=lambda acc, n: acc + n, stop_condition=6) == 6
    assert chi.next() == 4
    assert base == [1, 2, 3, 4, 5, 6]


def test_map_if():
    base = [1, 2, 3, 4, 5, 6]

    assert Chi(base).map_if(
        constraint=lambda n: n % 2 == 0, transformation=lambda n: n * 2
    ).collect(list) == [
        1,
        4,
        3,
        8,
        5,
        12,
    ]
    assert base == [1, 2, 3, 4, 5, 6]


def test_map_while():
    base = [1, 2, 3, 4, 5, 6]

    assert Chi(base).map_while(constraint=lambda n: n < 4, transformation=lambda n: n * 2).collect(
        list
    ) == [
        2,
        4,
        6,
        4,
        5,
        6,
    ]
    assert base == [1, 2, 3, 4, 5, 6]


def test_flatten():

    base = [1]
    assert Chi(base).flatten().collect(list) == [1]
    base = [[1]]
    assert Chi(base).flatten().collect(list) == [1]
    base = [[[1]]]
    assert Chi(base).flatten().collect(list) == [1]
    base = [[[[1]]]]
    assert Chi(base).flatten().collect(list) == [1]
    base = [[1], [[2, 3]], [[4, [5, 6]]], [7, [8, [9, [10, [11]]]]]]
    assert Chi(base).flatten().collect(list) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    assert base == [[1], [[2, 3]], [[4, [5, 6]]], [7, [8, [9, [10, [11]]]]]]

    base = [(1)]
    assert Chi(base).flatten(stop_condition=lambda elem: isinstance(elem, Tuple)).collect(list) == [(1)]
    base = [[(1)]]
    assert Chi(base).flatten(stop_condition=lambda elem: isinstance(elem, Tuple)).collect(list) == [(1)]
    base = [[[(1)]]]
    assert Chi(base).flatten(stop_condition=lambda elem: isinstance(elem, Tuple)).collect(list) == [(1)]
    base = [[[[(1)]]]]
    assert Chi(base).flatten(stop_condition=lambda elem: isinstance(elem, Tuple)).collect(list) == [(1)]
    base = [[1], [[(2, 3)]], [[(4, [5, 6])]], [7, [8, [9, [10, [11]]]]]]
    assert Chi(base).flatten(stop_condition=lambda elem: isinstance(elem, Tuple)).collect(list) == [1, (2, 3), (4, [5, 6]), 7, 8, 9, 10, 11]

def test_consumation():
    base = [1, 2, 3, 4, 5, 6]

    chi = Chi(base)
    chi.collect(list)

    with pytest.raises(StopIteration):
        for e in chi:
            pass

    chi = Chi(base)
    for e in chi:
        pass
    with pytest.raises(StopIteration):
        chi.collect(set)

    assert base == [1, 2, 3, 4, 5, 6]


def test_yield_from():
    def inner_fn(chi: Chi) -> Generator[Any, None, None]:
        yield from chi

    base = [1, 2, 3, 4, 5, 6]
    res = []
    counter = 0
    for elem in inner_fn(Chi(base)):
        res.append(elem)
        counter += 1

    assert counter == 6

    assert base == [1, 2, 3, 4, 5, 6]
    assert base == res


def test_sum():
    base = [1, 2, 3, 4, 5, 6]
    assert Chi(base).sum() == sum(base)


def test_max():
    base = [1, 2, 3, 4, 5, 6]
    assert Chi(base).max() == max(base)


def test_min():
    base = [1, 2, 3, 4, 5, 6]
    assert Chi(base).min() == min(base)


def test_avg():
    base = [1, 2, 3, 4, 5, 6]
    assert Chi(base).avg() == sum(base) / len(base)


def test_len():
    base = [1, 2, 3, 4, 5, 6]
    chi = Chi(base)

    assert len(chi) == 6

    chi.filter(lambda n: n % 2 == 0)
    assert len(chi) == 3

    chi = Chi(base).skip(2)
    assert len(chi) == 4
