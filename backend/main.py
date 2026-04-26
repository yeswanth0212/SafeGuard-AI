from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import models, schemas, auth
from database import engine, Base, SessionLocal
import json

Base.metadata.create_all(bind=engine)

app = FastAPI()

clients = {}

# DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- AUTH ---------------- #

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    return {"msg": "Registered"}

@app.post("/login")
def login(data: schemas.Login, db: Session = Depends(get_db)):
    user = auth.authenticate(db, data.username, data.password)
    if not user:
        return {"error": "Invalid"}
    return {
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "age": user.age,
            "role": user.role,
            "profile_photo": user.profile_photo
        }
    }

@app.get("/admin/active-users")
def active_users(db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.status == "ACTIVE").all()

# ---------------- WEBSOCKET ---------------- #

@app.websocket("/ws/{client_id}")
async def websocket(ws: WebSocket, client_id: str):
    await ws.accept()
    clients[client_id] = ws

    db = SessionLocal()

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            user = None
            if client_id != "admin":
                user = db.query(models.User).filter(models.User.id == int(client_id)).first()

            # SOS START
            if msg["type"] == "sos_start":
                user.status = "ACTIVE"
                db.commit()

                if "admin" in clients:
                    await clients["admin"].send_json({
                        "type": "sos_start",
                        "user": {
                            "id": user.id,
                            "full_name": user.full_name,
                            "age": user.age,
                            "profile_photo": user.profile_photo,
                            "lat": user.lat,
                            "lng": user.lng
                        }
                    })

            # LOCATION UPDATE
            if msg["type"] == "location_update":
                user.lat = str(msg["lat"])
                user.lng = str(msg["lng"])
                db.commit()

                if "admin" in clients:
                    await clients["admin"].send_json({
                        "type": "location_update",
                        "user_id": user.id,
                        "lat": user.lat,
                        "lng": user.lng
                    })

            # SOS STOP
            if msg["type"] == "sos_stop":
                user.status = "INACTIVE"
                db.commit()

                if "admin" in clients:
                    await clients["admin"].send_json({
                        "type": "sos_stop",
                        "user_id": user.id
                    })

            # WEBRTC SIGNALING
            if msg["type"].startswith("webrtc"):
                target = str(msg["to"])
                if target in clients:
                    await clients[target].send_json(msg)

    except WebSocketDisconnect:
        del clients[client_id]
