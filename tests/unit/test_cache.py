"""
Unit tests for Collection and CacheManager classes.
"""

import asyncio

from mezon.managers.cache import CacheManager, Collection


class TestCollection:
    """Test Collection class."""

    def test_init_creates_empty_collection(self):
        """Test that initialization creates empty collection."""
        collection = Collection()
        assert collection.size == 0
        assert len(collection) == 0

    def test_set_and_get(self):
        """Test setting and getting values."""
        collection = Collection()
        collection.set("key1", "value1")
        collection.set("key2", "value2")

        assert collection.get("key1") == "value1"
        assert collection.get("key2") == "value2"
        assert collection.size == 2

    def test_get_nonexistent_returns_none(self):
        """Test that getting nonexistent key returns None."""
        collection = Collection()
        assert collection.get("nonexistent") is None

    def test_delete_existing_key(self):
        """Test deleting an existing key."""
        collection = Collection()
        collection.set("key1", "value1")

        result = collection.delete("key1")

        assert result is True
        assert collection.get("key1") is None
        assert collection.size == 0

    def test_delete_nonexistent_key(self):
        """Test deleting a nonexistent key."""
        collection = Collection()
        result = collection.delete("nonexistent")
        assert result is False

    def test_first_returns_first_value(self):
        """Test that first returns the first value."""
        collection = Collection()
        collection.set("key1", "first")
        collection.set("key2", "second")
        collection.set("key3", "third")

        assert collection.first() == "first"

    def test_first_on_empty_returns_none(self):
        """Test that first on empty collection returns None."""
        collection = Collection()
        assert collection.first() is None

    def test_first_key_returns_first_key(self):
        """Test that first_key returns the first key."""
        collection = Collection()
        collection.set("alpha", 1)
        collection.set("beta", 2)
        collection.set("gamma", 3)

        assert collection.first_key() == "alpha"

    def test_first_key_on_empty_returns_none(self):
        """Test that first_key on empty collection returns None."""
        collection = Collection()
        assert collection.first_key() is None

    def test_filter(self):
        """Test filtering collection."""
        collection = Collection()
        collection.set("key1", 10)
        collection.set("key2", 20)
        collection.set("key3", 30)
        collection.set("key4", 40)

        filtered = collection.filter(lambda v: v > 20)

        assert filtered.size == 2
        assert filtered.get("key3") == 30
        assert filtered.get("key4") == 40
        assert filtered.get("key1") is None

    def test_map(self):
        """Test mapping over collection."""
        collection = Collection()
        collection.set("key1", 1)
        collection.set("key2", 2)
        collection.set("key3", 3)

        result = collection.map(lambda v: v * 2)

        assert result == [2, 4, 6]

    def test_values_iterator(self):
        """Test values iterator."""
        collection = Collection()
        collection.set("key1", "a")
        collection.set("key2", "b")
        collection.set("key3", "c")

        values = list(collection.values())

        assert values == ["a", "b", "c"]

    def test_keys_iterator(self):
        """Test keys iterator."""
        collection = Collection()
        collection.set("key1", "a")
        collection.set("key2", "b")
        collection.set("key3", "c")

        keys = list(collection.keys())

        assert keys == ["key1", "key2", "key3"]

    def test_items_iterator(self):
        """Test items iterator."""
        collection = Collection()
        collection.set("key1", "a")
        collection.set("key2", "b")

        items = list(collection.items())

        assert items == [("key1", "a"), ("key2", "b")]

    def test_clear(self):
        """Test clearing collection."""
        collection = Collection()
        collection.set("key1", "value1")
        collection.set("key2", "value2")

        assert collection.size == 2

        collection.clear()

        assert collection.size == 0
        assert collection.get("key1") is None

    def test_contains(self):
        """Test __contains__ method."""
        collection = Collection()
        collection.set("key1", "value1")

        assert "key1" in collection
        assert "key2" not in collection

    def test_iter(self):
        """Test __iter__ method."""
        collection = Collection()
        collection.set("key1", "a")
        collection.set("key2", "b")
        collection.set("key3", "c")

        keys = list(collection)

        assert keys == ["key1", "key2", "key3"]

    def test_len(self):
        """Test __len__ method."""
        collection = Collection()
        assert len(collection) == 0

        collection.set("key1", "value1")
        assert len(collection) == 1

        collection.set("key2", "value2")
        assert len(collection) == 2

    def test_maintains_insertion_order(self):
        """Test that collection maintains insertion order."""
        collection = Collection()
        collection.set("z", 1)
        collection.set("a", 2)
        collection.set("m", 3)

        keys = list(collection.keys())
        assert keys == ["z", "a", "m"]


class TestCacheManager:
    """Test CacheManager class."""

    def test_init_creates_empty_cache(self):
        """Test that initialization creates empty cache."""

        async def fetcher(key):
            return f"value_{key}"

        cache = CacheManager(fetcher)
        assert cache.size == 0

    def test_get_from_empty_cache(self):
        """Test getting from empty cache returns None."""

        async def fetcher(key):
            return f"value_{key}"

        cache = CacheManager(fetcher)
        assert cache.get("key1") is None

    def test_set_and_get(self):
        """Test setting and getting values."""

        async def fetcher(key):
            return f"value_{key}"

        cache = CacheManager(fetcher)
        cache.set("key1", "value1")

        assert cache.get("key1") == "value1"
        assert cache.size == 1

    def test_fetch_from_cache(self):
        """Test fetching value that exists in cache."""

        async def test():
            call_count = []

            async def fetcher(key):
                call_count.append(key)
                return f"value_{key}"

            cache = CacheManager(fetcher)
            cache.set("key1", "cached_value")

            result = await cache.fetch("key1")

            assert result == "cached_value"
            assert len(call_count) == 0  # Fetcher should not be called

        asyncio.run(test())

    def test_fetch_not_in_cache(self):
        """Test fetching value that doesn't exist in cache."""

        async def test():
            async def fetcher(key):
                return f"fetched_{key}"

            cache = CacheManager(fetcher)
            result = await cache.fetch("key1")

            assert result == "fetched_key1"
            assert cache.get("key1") == "fetched_key1"  # Should be cached now

        asyncio.run(test())

    def test_max_size_eviction(self):
        """Test that cache evicts oldest item when max size is reached."""

        async def fetcher(key):
            return f"value_{key}"

        cache = CacheManager(fetcher, max_size=3)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        assert cache.size == 3

        # Adding 4th item should evict the first
        cache.set("key4", "value4")

        assert cache.size == 3
        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_unlimited_cache_size(self):
        """Test cache with unlimited size."""

        async def fetcher(key):
            return f"value_{key}"

        cache = CacheManager(fetcher)  # No max_size specified

        for i in range(100):
            cache.set(f"key{i}", f"value{i}")

        assert cache.size == 100

    def test_first(self):
        """Test getting first value from cache."""

        async def fetcher(key):
            return f"value_{key}"

        cache = CacheManager(fetcher)
        cache.set("key1", "first")
        cache.set("key2", "second")

        assert cache.first() == "first"

    def test_filter(self):
        """Test filtering cache."""

        async def fetcher(key):
            return key

        cache = CacheManager(fetcher)
        cache.set("key1", 10)
        cache.set("key2", 20)
        cache.set("key3", 30)

        filtered = cache.filter(lambda v: v >= 20)

        assert filtered.size == 2
        assert filtered.get("key2") == 20
        assert filtered.get("key3") == 30

    def test_map(self):
        """Test mapping over cache."""

        async def fetcher(key):
            return key

        cache = CacheManager(fetcher)
        cache.set("key1", 1)
        cache.set("key2", 2)
        cache.set("key3", 3)

        result = cache.map(lambda v: v * 10)

        assert result == [10, 20, 30]

    def test_values(self):
        """Test getting values iterator."""

        async def fetcher(key):
            return key

        cache = CacheManager(fetcher)
        cache.set("key1", "a")
        cache.set("key2", "b")

        values = list(cache.values())

        assert values == ["a", "b"]

    def test_delete(self):
        """Test deleting from cache."""

        async def fetcher(key):
            return key

        cache = CacheManager(fetcher)
        cache.set("key1", "value1")

        result = cache.delete("key1")

        assert result is True
        assert cache.get("key1") is None

    def test_clear(self):
        """Test clearing cache."""

        async def fetcher(key):
            return key

        cache = CacheManager(fetcher)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.size == 0

    def test_has(self):
        """Test checking if key exists in cache."""

        async def fetcher(key):
            return key

        cache = CacheManager(fetcher)
        cache.set("key1", "value1")

        assert cache.has("key1") is True
        assert cache.has("key2") is False

    def test_fetch_multiple_times(self):
        """Test fetching same key multiple times uses cache."""

        async def test():
            call_count = []

            async def fetcher(key):
                call_count.append(key)
                return f"value_{key}"

            cache = CacheManager(fetcher)

            result1 = await cache.fetch("key1")
            result2 = await cache.fetch("key1")
            result3 = await cache.fetch("key1")

            assert result1 == result2 == result3 == "value_key1"
            assert len(call_count) == 1  # Fetcher called only once

        asyncio.run(test())
