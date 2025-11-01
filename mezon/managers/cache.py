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

from typing import (
    TypeVar,
    Generic,
    Optional,
    Callable,
    Iterator,
    List,
    Awaitable,
)
from collections import OrderedDict

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

    def get(self, key: K) -> Optional[V]:
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

    def first(self) -> Optional[V]:
        """
        Get the first value in the collection.

        Returns:
            The first value if the collection is not empty, None otherwise
        """
        if not self._data:
            return None
        return next(iter(self._data.values()))

    def first_key(self) -> Optional[K]:
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

    def map(self, fn: Callable[[V], T]) -> List[T]:
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

    @property
    def size(self) -> int:
        """Get the current cache size."""
        return self.cache.size

    def get(self, id: K) -> Optional[V]:
        """
        Get a value from the cache by ID.

        Args:
            id: The key to look up

        Returns:
            The cached value if found, None otherwise
        """
        return self.cache.get(id)

    def set(self, id: K, value: V) -> None:
        """
        Set a value in the cache.

        If the cache is at max capacity, the oldest item is evicted first.

        Args:
            id: The key
            value: The value to cache
        """
        if self._max_size is not None and self.cache.size >= self._max_size:
            first_key = self.cache.first_key()
            if first_key is not None:
                self.cache.delete(first_key)

        self.cache.set(id, value)

    async def fetch(self, id: K) -> V:
        """
        Fetch a value by ID, using the cache if available.

        If the value is not in the cache, it will be fetched using
        the fetcher function and then cached.

        Args:
            id: The key to fetch

        Returns:
            The value (from cache or freshly fetched)
        """
        existing = self.get(id)
        if existing is not None:
            return existing

        fetched = await self._fetcher(id)
        self.set(id, fetched)
        return fetched

    def first(self) -> Optional[V]:
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

    def map(self, fn: Callable[[V], T]) -> List[T]:
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
