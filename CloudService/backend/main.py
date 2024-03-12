from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["*"],
)


@app.get('/')
def home():
    return {"data": "Hello world!"}


@app.get("/devices/{name}")
async def device_by_name(
    name: str, db: db_dependency
):
    """
    :param db:
    :param name:
    :return: Device
    """
    print('asd', name)
    result = db.query(models.Device).filter(models.Device.name == name).first()
    if not result:
        raise HTTPException(status_code=404, detail=f"Устройство не найдено: {name}")
    return result


@app.post("/devices")
async def add_device(device: models.DeviceBase, db: db_dependency):
    dev = models.Device(name=device.name, ip=device.ip, category=device.category)
    db.add(dev)
    db.commit()
    db.refresh(dev)


@app.get("/all_devices")
async def get_devices(db: db_dependency):
    result = db.query(models.Device).all()
    if not result:
        raise HTTPException(status_code=404, detail=f"Устройств не найдено.")
    return result

