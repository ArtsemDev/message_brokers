import contextlib

from fastapi import FastAPI, Depends
from faststream.rabbit import RabbitBroker, RabbitQueue
from pydantic import BaseModel
from starlette.requests import Request

broker = RabbitBroker(url="amqp://user:password@rabbit:5672")


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.connect()
    await broker.declare_queue(queue=RabbitQueue(name="log", durable=True))
    yield
    await broker.close()


class RequestDTO(BaseModel):
    url: str
    method: str
    headers: dict


async def amqp_logger(request: Request):
    await broker.publish(
        queue="log",
        message=RequestDTO(
            url=f"{request.url}",
            method=request.method,
            headers={**request.headers}
        ),
        content_type="application/json",
        content_encoding="utf-8"
    )


AMQPLogger = Depends(dependency=amqp_logger)


app = FastAPI(lifespan=lifespan, dependencies=[AMQPLogger])


@app.get(path="/")
async def index():
    return "OK"


if __name__ == '__main__':
    from uvicorn import run
    run(app=app, host="0.0.0.0", port=80)
