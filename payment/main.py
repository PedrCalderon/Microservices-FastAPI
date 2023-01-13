from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests, time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

# This should be different database
redis = get_redis_connection(
    host="redis-19569.c55.eu-central-1-1.ec2.cloud.redislabs.com",
    port=19569,
    password="m0LkSKI4Gyv2N7PYTkvuUKF18Z9vjkG3",
    decode_responses=True
)

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str # pending, completed, refunded

    class Meta:
        database = redis

@app.post('/orders')
async def create(request: Request, background_tasks: BackgroundTasks):   # id, quantity
    body = await request.json()

    req = requests.get('http://localhost:8000/products/%s' % body['id'])
    product = req.json()

    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2 * product['price'],
        total=1.2 * product['price'],
        quantity=body['quantity'],
        status='pending'
    )
    order.save()

    order_completed(order)

    return order


def order_completed(order: Order):
    order.status = 'completed'
    order.save()

