from fastapi import FastAPI, WebSocket,BackgroundTasks
import json
from fastapi.middleware.cors import CORSMiddleware
from aiokafka import AIOKafkaProducer,AIOKafkaConsumer
from contextlib import asynccontextmanager
import asyncio
from typing import Dict,DefaultDict,Set
from collections import defaultdict
from fastapi_mail import FastMail,MessageSchema,ConnectionConfig
import os
from dotenv import load_dotenv
import math
from sqlmodel import Session
from sqlalchemy import create_engine,Select
from models import UserInDB,RouteAnArea
from typing import Optional
load_dotenv()

ele = os.getenv("db_url")
db_url = ele
db = create_engine(db_url)

producer = None
consumer = None
connected_clients: Dict[str, Set[WebSocket]] = defaultdict(set)
print(connected_clients)

async def consume_and_broadcast():
    global consumer
    async for msg in consumer:
        try:
            msg_str = msg.value.decode()
            data = json.loads(msg_str)
            await consume_message_calculate(data)
            rid = str(data.get("route_id"))
            print(f"Kafka msg for route {rid}: {msg_str}")

            for client in connected_clients.get(rid, set()).copy():
                try:
                    await client.send_text(msg_str)
                except:
                    connected_clients[rid].remove(client)
        except Exception as e:
            print("Error processing message:", e)



@asynccontextmanager
async def lifespan(app:FastAPI):
    global producer,consumer
    producer = AIOKafkaProducer(bootstrap_servers="localhost:9093")
    await producer.start()
    print("kafka producer start")
    consumer = AIOKafkaConsumer("send_notification", bootstrap_servers="localhost:9093")
    await consumer.start()
    print("consumer started")
    task = asyncio.create_task(consume_and_broadcast())

    yield  # This runs the app while background task runs

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    await consumer.stop()
    await producer.stop()
    print("Kafka stopped")


    

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)
# connected_clients = []

@app.websocket("/realtime")
async def get_realtime_location(websocket: WebSocket):
    await websocket.accept()
    # connected_clients.append(websocket)
    print("Client connected")

    try:
        while True:
            data = await websocket.receive_text()
            print("Received GPS:", data)
            await producer.send_and_wait("send_notification", data.encode())
            await producer.send_and_wait("eta_data",data.encode())
            await producer.send_and_wait("logss",data.encode())



            # Broadcast to all connected clients (except sender)
            # for client in connected_clients:
            #     if client != websocket:
            #         await client.send_text(data)

    except Exception as e:
        print("WebSocket disconnected:", e)
    # finally:
    #     connected_clients.remove(websocket)

# connected_clients: Dict[str,set[WebSocket]]

@app.websocket('/sendd/{rid}')
async def map_update_stream(websocket: WebSocket, rid: int):
    await websocket.accept()
    print(f"Map client connected for route {rid}")
    rid = str(rid)
    connected_clients[rid].add(websocket)

    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except Exception:
        print(f"Client disconnected from route {rid}")
    finally:
        connected_clients[rid].discard(websocket)
        if not connected_clients[rid]:
            del connected_clients[rid]

    
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME") ,
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM="shrushtikale5@gmail.com",
    MAIL_PORT= 587,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_SSL_TLS=False,
    MAIL_STARTTLS=True,
    USE_CREDENTIALS= True

)
from typing import Optional, List
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema
import math
import asyncio

# Configured somewhere globally
fm = FastMail(conf)

# 1. Send Email Function
def send_user_email(recipients: List[str], body: str, background_tasks: Optional[BackgroundTasks] = None):
    message = MessageSchema(
        subject="Regarding ETA",
        recipients=recipients,
        body=body,
        subtype="plain"
    )

    if background_tasks:
        background_tasks.add_task(fm.send_message, message)
    else:
        # If running outside FastAPI, fallback to async dispatch
        asyncio.create_task(fm.send_message(message))

    return "Message sent"

# 2. Haversine Function
def haversine(lat1, lon1, lat2, lon2, email, background_tasks: Optional[BackgroundTasks] = None):
    R = 6371  # Earth radius in km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    ETA = 1.0765 + 1.9570 * distance
    print(ETA)

    if ETA <= 10:

        send_user_email([email], f"Driver is {ETA:.2f} minutes away.", background_tasks)

    return distance

# 3. Kafka Consumer Processing
async def consume_message_calculate(data, background_tasks: Optional[BackgroundTasks] = None):
    print("into cpnsume")
    driver_lat = data.get("lat")
    driver_lng = data.get("lng")
    route_id = data.get("route_id")
    print(route_id)

    with Session(db) as session:
        areas = session.exec(Select(RouteAnArea.area).where(RouteAnArea.route_id == route_id)).all()
        print(areas)
        for area_name in areas:
            print(area_name[0])
            users = session.exec(Select(UserInDB).where(UserInDB.full_name == area_name[0])).all()

            if users:
                for user in users:

                    print(user)
                    haversine(driver_lat, driver_lng, user[0].lat, user[0].lon, user[0].email, background_tasks)




    
    





    
    







