from asyncio import sleep
from logging import getLogger

from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue
from pydantic import BaseModel

logger = getLogger(__name__)
broker = RabbitBroker(url="amqp://user:password@rabbit:5672")
app = FastStream(broker=broker)


async def start_up():
    await broker.connect()
    await broker.declare_queue(queue=RabbitQueue(name="log", passive=True))


app.on_startup(start_up)


class RequestDTO(BaseModel):
    url: str
    method: str
    headers: dict


@broker.subscriber(queue="log")
async def _logger(body: RequestDTO):
    await sleep(2)
    logger.warning("CONSUMING")
    logger.warning(body)
