"""
Copyright 2020 The Mezon Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import asyncio
from collections import OrderedDict
from collections.abc import Awaitable, Callable, Iterator
from typing import (
    Generic,
    TypeVar,
)

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")


class Collection(Generic[K, V]):
    """
    A collection data structure similar to JavaScript's Map with additional utility methods.

    This class maintains insertion order and provides methods for filtering, mapping, and iteration.
    """

    def __init__(self):
        """Initialize an empty collection."""
        self._data: OrderedDict[K, V] = OrderedDict()

    @property
    def size(self) -> int:
        """Get the number of items in the collection."""
        return len(self._data)

    def get(self, key: K) -> V | None:
        """
        Get a value by key.

        Args:
            key: The key to look up

        Returns:
            The value if found, None otherwise
        """
        return self._data.get(key)

    def set(self, key: K, value: V) -> None:
        """
        Set a key-value pair in the collection.

        Args:
            key: The key
            value: The value to store
        """
        self._data[key] = value

    def delete(self, key: K) -> bool:
        """
        Delete a key from the collection.

        Args:
            key: The key to delete

        Returns:
            True if the key was deleted, False if it didn't exist
        """
        if key in self._data:
            del self._data[key]
            return True
        return False

    def move_to_end(self, key: K) -> None:
        """Mark a key as most-recently-used by moving it to the end, if present."""
        if key in self._data:
            self._data.move_to_end(key)

    def first(self) -> V | None:
        """
        Get the first value in the collection.

        Returns:
            The first value if the collection is not empty, None otherwise
        """
        if not self._data:
            return None
        return next(iter(self._data.values()))

    def first_key(self) -> K | None:
        """
        Get the first key in the collection.

        Returns:
            The first key if the collection is not empty, None otherwise
        """
        if not self._data:
            return None
        return next(iter(self._data.keys()))

    def filter(self, fn: Callable[[V], bool]) -> "Collection[K, V]":
        """
        Filter the collection by a predicate function.

        Args:
            fn: A function that returns True for values to keep

        Returns:
            A new Collection containing only the filtered values
        """
        result = Collection[K, V]()
        for key, value in self._data.items():
            if fn(value):
                result.set(key, value)
        return result

    def map(self, fn: Callable[[V], T]) -> list[T]:
        """
        Map over the collection values.

        Args:
            fn: A function to transform each value

        Returns:
            A list of transformed values
        """
        return [fn(value) for value in self._data.values()]

    def values(self) -> Iterator[V]:
        """
        Get an iterator over the collection values.

        Returns:
            An iterator over values
        """
        return iter(self._data.values())

    def keys(self) -> Iterator[K]:
        """
        Get an iterator over the collection keys.

        Returns:
            An iterator over keys
        """
        return iter(self._data.keys())

    def items(self) -> Iterator[tuple[K, V]]:
        """
        Get an iterator over key-value pairs.

        Returns:
            An iterator over (key, value) tuples
        """
        return iter(self._data.items())

    def clear(self) -> None:
        """Clear all items from the collection."""
        self._data.clear()

    def __contains__(self, key: K) -> bool:
        """Check if a key exists in the collection."""
        return key in self._data

    def __iter__(self) -> Iterator[K]:
        """Iterate over keys."""
        return iter(self._data.keys())

    def __len__(self) -> int:
        """Get the number of items in the collection."""
        return len(self._data)


class CacheManager(Generic[K, V]):
    """
    A cache manager with automatic fetching and LRU-like eviction.

    This class manages a cache of items with a maximum size limit.
    When the cache is full, the oldest item is evicted (FIFO strategy).
    """

    def __init__(
        self,
        fetcher: Callable[[K], Awaitable[V]],
        max_size: int = float("inf"),
    ):
        """
        Initialize the cache manager.

        Args:
            fetcher: An async function that fetches a value by key
            max_size: Maximum number of items to cache (default: unlimited)
        """
        self.cache: Collection[K, V] = Collection()
        self._fetcher = fetcher
        self._max_size = max_size if max_size != float("inf") else None
        self._in_flight: dict[K, asyncio.Future[V]] = {}

    @property
    def size(self) -> int:
        """Get the current cache size."""
        return self.cache.size

    def get(self, id: K) -> V | None:
        """
        Get a value from the cache by ID.

        Marks the entry as most-recently-used on a hit, so `set`'s eviction
        is genuinely LRU rather than pure insertion-order FIFO.

        Args:
            id: The key to look up

        Returns:
            The cached value if found, None otherwise
        """
        value = self.cache.get(id)
        if value is not None:
            self.cache.move_to_end(id)
        return value

    def set(self, id: K, value: V) -> None:
        """
        Set a value in the cache.

        If the cache is at max capacity, the least-recently-used item is
        evicted first.

        Args:
            id: The key
            value: The value to cache
        """
        if (
            self._max_size is not None
            and self.cache.size >= self._max_size
            and id not in self.cache
        ):
            lru_key = self.cache.first_key()
            if lru_key is not None:
                self.cache.delete(lru_key)

        self.cache.set(id, value)
        self.cache.move_to_end(id)

    async def fetch(self, id: K) -> V:
        """
        Fetch a value by ID, using the cache if available.

        If the value is not in the cache, it will be fetched using the
        fetcher function and then cached. Concurrent fetches for the same
        uncached id share a single in-flight call instead of each firing
        their own request against the fetcher.

        Args:
            id: The key to fetch

        Returns:
            The value (from cache or freshly fetched)
        """
        existing = self.get(id)
        if existing is not None:
            return existing

        in_flight = self._in_flight.get(id)
        if in_flight is not None:
            return await in_flight

        future: asyncio.Future[V] = asyncio.get_running_loop().create_future()
        self._in_flight[id] = future
        try:
            fetched = await self._fetcher(id)
        except BaseException as exc:
            future.set_exception(exc)
            raise
        else:
            self.set(id, fetched)
            future.set_result(fetched)
            return fetched
        finally:
            del self._in_flight[id]

    def first(self) -> V | None:
        """
        Get the first value in the cache.

        Returns:
            The first cached value if cache is not empty, None otherwise
        """
        return self.cache.first()

    def filter(self, fn: Callable[[V], bool]) -> Collection[K, V]:
        """
        Filter the cache by a predicate function.

        Args:
            fn: A function that returns True for values to keep

        Returns:
            A new Collection containing only the filtered values
        """
        return self.cache.filter(fn)

    def map(self, fn: Callable[[V], T]) -> list[T]:
        """
        Map over the cache values.

        Args:
            fn: A function to transform each value

        Returns:
            A list of transformed values
        """
        return self.cache.map(fn)

    def values(self) -> Iterator[V]:
        """
        Get an iterator over the cache values.

        Returns:
            An iterator over cached values
        """
        return self.cache.values()

    def delete(self, id: K) -> bool:
        """
        Delete a value from the cache.

        Args:
            id: The key to delete

        Returns:
            True if the key was deleted, False if it didn't exist
        """
        return self.cache.delete(id)

    def clear(self) -> None:
        """Clear all items from the cache."""
        self.cache.clear()

    def has(self, id: K) -> bool:
        """
        Check if a key exists in the cache.

        Args:
            id: The key to check

        Returns:
            True if the key exists, False otherwise
        """
        return id in self.cache
