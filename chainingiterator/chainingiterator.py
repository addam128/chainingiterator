from typing import Iterator, Iterable, Collection, Any, Callable, Optional, Generator, Tuple, Sized
from math import inf


class ChainingIterator(Iterator, Sized):
    """



    size: autoset if we create Chi from a Sized object, else must be computed on the fly
          methods changing the lenght of the iterator must set the iterator to the right value
          or to None, indicating that new on-the-fly computation is needed - done on request
    """

    def __init__(self, base: Iterable) -> None:
        self._iter: Iterator = iter(base)
        self._consumed = False
        self._size = len(base) if isinstance(base, Sized) else None

    def __consumed_guard(self):
        if self._consumed:
            raise StopIteration("ChainingIterator has been already consumed.")

    def __iter__(self):
        self.__consumed_guard()
        return self

    def __next__(self):
        self.__consumed_guard()
        try:
            self._size = None  # we move the iterator, size info must not hold after this
            return next(self._iter)
        except StopIteration:
            self._consumed = True
            raise StopIteration

    def map(self, func: Callable) -> "ChainingIterator":
        self.__consumed_guard()
        self._iter = map(func, self._iter)
        return self

    def filter(self, func: Callable) -> "ChainingIterator":
        self.__consumed_guard()
        self._iter = filter(func, self._iter)
        self._size = None
        return self

    def any(self, predicate: Callable) -> bool:
        self.__consumed_guard()
        self.map(predicate)
        self._consumed = True
        return any(self._iter)

    def all(self, predicate: Callable) -> bool:
        self.__consumed_guard()
        self.map(predicate)
        self._consumed = True
        return all(self._iter)

    def next(self) -> Any:
        return self.__next__()

    def next_chunk(self, size: int) -> Iterable:
        self.__consumed_guard()
        res = []
        for _ in range(size):
            try:
                res.append(self.next())
            except Exception:
                self._consumed = True
                break
        self._size = None
        return res

    def foreach(self, func: Callable) -> None:
        self.__consumed_guard()
        for elem in self._iter:
            func(elem)
        self._consumed = True

    def zip(self, other: Iterator) -> "ChainingIterator":
        self.__consumed_guard()
        self._iter = zip(self._iter, other)
        return self

    def enumerate(self) -> "ChainingIterator":
        self.__consumed_guard()
        self._iter = enumerate(self._iter)
        return self

    def nth(self, n: int) -> Any:
        self.__consumed_guard()
        try:
            item = next(self._iter)
            for _ in range(n):
                item = next(self._iter)
            self._consumed = True
            return item
        except StopIteration:
            raise IndexError

    def count(self) -> int:
        self.__consumed_guard()
        count = 0
        for elem in self._iter:
            count += 1
        self._consumed = True
        return count

    def chain(self, other: Iterator) -> "ChainingIterator":
        def _chain(first: Iterator, second: Iterator) -> Iterator:
            try:
                yield from first
            except StopIteration:
                pass
            except RuntimeError as e:
                # print(e)
                pass
            try:
                yield from second
            except StopIteration:
                return
            except RuntimeError as e:
                # print(e)
                return

        self.__consumed_guard()
        self._iter = _chain(self._iter, other)
        self._size = None
        return self

    def take_while(self, func: Callable) -> "ChainingIterator":
        def taker(iter: Iterator, func: Callable) -> Iterator:
            for elem in iter:
                if func(elem):
                    yield elem
                else:
                    return

        self.__consumed_guard()
        self._iter = taker(self._iter, func)
        self._size = None
        return self

    def skip_while(self, func: Callable) -> "ChainingIterator":
        def skipper(iter: Iterator, func: Callable) -> Iterator:
            for elem in iter:
                if func(elem):
                    continue
                break
            return iter

        self.__consumed_guard()
        self._iter = skipper(self._iter, func)
        self._size = None
        return self

    def discard(self) -> "ChainingIterator":
        for _ in self._iter:
            pass
        self._consumed = True
        return self

    def find_first(self, predicate: Callable) -> Any:
        self.__consumed_guard()
        self._consumed = True
        for elem in self._iter:
            if predicate(elem):
                self.discard()
                return elem

    def index(self, predicate: Callable) -> Optional[int]:
        self.__consumed_guard()
        idx = 0
        for elem in self._iter:
            if predicate(elem):
                self.discard()
                return idx
            idx += 1
        self._consumed = True
        return None

    def take(self, count: int) -> "ChainingIterator":
        def taker(iter: Iterator, count: int) -> Iterator:
            n = 0
            for elem in iter:
                if n < count:
                    yield elem
                    n += 1
                    continue
                break

        self.__consumed_guard()
        self._iter = taker(self._iter, count)
        self._size = None  # We can not set count, as we may have less left in the iterator
        return self

    def step_by(self, n: int) -> "ChainingIterator":
        def stepper(iter: Iterator, n: int) -> Iterator:
            counter = 0
            for elem in iter:
                if counter % n == 0:
                    yield elem
                counter += 1

        self.__consumed_guard()
        self._iter = stepper(self._iter, n)
        self._size = None
        return self

    def skip(self, count: int) -> "ChainingIterator":
        def skipper(iterator: Iterator, count: int) -> Iterator:
            if count == 0:
                return iterator
            counter = 1
            for elem in iterator:
                if counter >= count:
                    return iterator
                counter += 1
            return iter([])

        self.__consumed_guard()
        self._iter = skipper(self._iter, count)
        self._size = self._size - count if self._size is not None else None
        return self

    def intersperse(self, elem: Any) -> "ChainingIterator":
        def isperser(iter: Iterator, divider: Any) -> Iterator:
            for elem in iter:
                yield elem
                yield divider

        self.__consumed_guard()
        self._iter = isperser(self._iter, elem)
        self._size = self._size * 2 if self._size is not None else None
        return self

    def last(self) -> Any:
        self.__consumed_guard()
        res = None
        for elem in self._iter:
            res = elem
        self._consumed = True
        return res

    def foldl(
        self,
        accumulator: Any,
        func: Callable,
        stop_condition: Optional[Any] = None,
    ) -> Any:
        self.__consumed_guard()
        try:
            if stop_condition is None:
                for elem in self._iter:
                    accumulator = func(accumulator, elem)
                self._consumed = True
                return accumulator
            # else
            for elem in self._iter:
                accumulator = func(accumulator, elem)
                if accumulator == stop_condition:
                    break
        except RuntimeError as e:
            pass
        finally:
            return accumulator

    def map_while(self, constraint: Callable, transformation: Callable) -> "ChainingIterator":
        def choosy_map_fastfail(
            olditer: Iterator, constraint: Callable, transformation: Callable
        ) -> Iterator:
            for elem in olditer:
                if constraint(elem):
                    yield transformation(elem)
                else:
                    yield elem
                    yield from olditer
                    return

        self.__consumed_guard()
        self._iter = choosy_map_fastfail(self._iter, constraint, transformation)
        self._size = None
        return self

    def map_if(self, constraint: Callable, transformation: Callable) -> "ChainingIterator":
        def choosy_map(
            olditer: Iterator, constraint: Callable, transformation: Callable
        ) -> Iterator:
            for elem in olditer:
                if constraint(elem):
                    yield transformation(elem)
                else:
                    yield elem

        self.__consumed_guard()
        self._iter = choosy_map(self._iter, constraint, transformation)
        return self

    def flatten(self, stop_condition: Optional[Callable] = None) -> "ChainingIterator":
        def inner_flatter(target: Any) -> Iterator:
            if not isinstance(target, Iterable) or (
                stop_condition is not None and stop_condition(target)
            ):
                yield target
                return
            for sub in target:
                yield from inner_flatter(sub)

        self.__consumed_guard()
        self._iter = inner_flatter(self._iter)
        self._size = None
        return self

    def inspect(self, inspector: Callable) -> "ChainingIterator":
        def inner_inspect(target: Iterator) -> Generator[Any, None, None]:
            for elem in target:
                inspector(elem)
                yield elem

        self.__consumed_guard()
        self._iter = inner_inspect(self._iter)
        return self

    def collect(self, constructor: Callable) -> Collection:
        self.__consumed_guard()
        self._consumed = True
        return constructor(self._iter)

    # TODO: partial eq type check

    def max(self) -> Any:
        return self.foldl(accumulator=-inf, func=lambda acc, val: max(acc, val))

    def min(self) -> Any:
        return self.foldl(accumulator=inf, func=lambda acc, val: min(acc, val))

    def sum(self) -> Any:
        return self.foldl(accumulator=0, func=lambda acc, val: acc + val)

    def avg(self) -> Any:
        def avger(accumulator: Tuple, elem: Any) -> Tuple:
            return accumulator[0] + elem, accumulator[1] + 1

        sum, count = self.foldl(accumulator=(0, 0), func=avger)
        return sum / count

    def __peek_length(self) -> int:
        """
        Based on som internet research, this is the best way to do this
        (better than itertools.tee)
        """
        lst = self.collect(list)
        length = len(lst)
        self._iter = iter(lst)
        self._size = length
        return self._size

    def __len__(self) -> int:
        self.__consumed_guard()
        return self._size if self._size is not None else self.__peek_length()
