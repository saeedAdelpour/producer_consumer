import asyncio
import pytest

from core import ProducerConsumer


def test_producer_consumer_class(Consumer):

    consumers = [Consumer(i) for i in range(2)]
    items = range(4)

    producer_consumer = ProducerConsumer(items, consumers)
    result = asyncio.run(producer_consumer.perform("run"))
    assert result == [(0, 0), (1, 1), (0, 2), (1, 3)]


@pytest.fixture
def Consumer():
    class __Consumer:
        def __init__(self, consumer_index) -> None:
            self.consumer_index = consumer_index

        async def run(self, item):
            await asyncio.sleep(0)
            return (self.consumer_index, item)

    return __Consumer