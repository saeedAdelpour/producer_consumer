import asyncio
import logging

from .exceptions import AllTasksFailedException


logger = logging.getLogger(__name__)


class TaskResult:
    fail = "fail"


class ProducerConsumer:
    def __init__(self, items, consumers) -> None:
        self.queue = asyncio.Queue()
        self.items = items
        self.consumers = consumers

    def produce_all(self):
        for item in self.items:
            self.queue.put_nowait(item)

    async def perform(self, consumer_method_name, args=tuple(), kwargs=dict()):
        self.produce_all()

        result = []
        try:
            await self.perform_consume(result, consumer_method_name, args, kwargs)
        except asyncio.exceptions.CancelledError:
            pass
        await self.queue.join()
        return result

    async def perform_consume(self, result, consumer_method_name, args, kwargs):
        tasks = [
            self.consume(result, getattr(consumer, consumer_method_name), args, kwargs)
            for consumer in self.consumers
        ]

        task_results = await asyncio.gather(*tasks)
        # write_report(session_objs)
        self.check_all_task_results(task_results)

    async def consume(self, result, method, args, kwargs):
        while True:
            # because we sure that queue will be filled completely, we can check queue.empty()
            if len(result) == len(self.items):
                self.cancel_tasks("consume")

            item = await self.queue.get()
            try:
                item_result = await method(item, *args, **kwargs)
                result.append(item_result)
                self.queue.task_done()
            except Exception:
                logger.exception("error")
                await self.queue.put(item)
                self.queue.task_done()
                return TaskResult.fail

    def cancel_tasks(self, task_name):
        tasks = asyncio.all_tasks()
        for task in tasks:
            coro = task.get_coro()
            if coro.__name__ == task_name:
                task.cancel()

    def check_all_task_results(self, task_results):
        """check all tasks are completed or failed, if all tasks failed, raise Exception"""
        failed_tasks = [t for t in task_results if t is TaskResult.fail]
        if len(failed_tasks) == len(task_results):
            raise AllTasksFailedException("all tasks failed")
