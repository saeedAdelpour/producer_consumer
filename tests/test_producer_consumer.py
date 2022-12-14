import asyncio
import pytest

from producer_consumer import ProducerConsumer
from producer_consumer.exceptions import AllTasksFailedException


def test_producer_consumer_class_if_all_success(create_new_event_loop, Consumer):
    consumers = [Consumer(i) for i in range(2)]
    items = range(4)

    producer_consumer = ProducerConsumer(items, consumers)
    result = asyncio.run(producer_consumer.perform("run"))
    assert result == [(0, 0), (1, 1), (0, 2), (1, 3)]


def test_producer_consumer_class_if_all_fail(create_new_event_loop, Consumer):
    consumers = [Consumer(i) for i in range(2)]
    items = range(4)
    producer_consumer = ProducerConsumer(items, consumers)
    with pytest.raises(AllTasksFailedException):
        asyncio.run(producer_consumer.perform("run_fail"))


def test_producer_consumer_class_if_one_task_ramin_and_first_consumer_fail(
    create_new_event_loop, Consumer
):
    consumers = [Consumer(i) for i in range(2)]
    items = range(1)
    producer_consumer = ProducerConsumer(items, consumers)
    result = asyncio.run(producer_consumer.perform("run_fail_on_index_0"))
    assert result == [(1, 0)]


def test_producer_consumer_class_check_default_prams_passing(
    create_new_event_loop, Consumer
):
    consumers = [Consumer(i) for i in range(2)]
    items = range(4)

    producer_consumer = ProducerConsumer(items, consumers)
    result = asyncio.run(
        producer_consumer.perform(
            "run_with_args",
            args=("arg1", "arg2"),
            kwargs={"a": "a", "b": "b"},
        ),
    )
    assert result == [
        (0, (0, "arg1", "arg2", "a", "b")),
        (1, (1, "arg1", "arg2", "a", "b")),
        (0, (2, "arg1", "arg2", "a", "b")),
        (1, (3, "arg1", "arg2", "a", "b")),
    ]


@pytest.fixture
def Consumer():
    class __Consumer:
        def __init__(self, consumer_index) -> None:
            self.consumer_index = consumer_index

        async def run(self, item):
            await asyncio.sleep(0)
            return (self.consumer_index, item)

        async def run_fail(self, item):
            raise Exception(str(item))

        async def run_fail_on_index_0(self, item):
            if self.consumer_index == 0:
                raise Exception("index fail")
            return await self.run(item)

        async def run_with_args(self, item, arg1, arg2, a, b):
            await asyncio.sleep(0)
            return (self.consumer_index, (item, arg1, arg2, a, b))

    return __Consumer


@pytest.fixture
def create_new_event_loop():
    """RuntimeError: There is no current event loop in thread 'MainThread'."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield
    loop.close()
