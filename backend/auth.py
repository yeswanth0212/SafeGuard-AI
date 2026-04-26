from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate(db, username, password):
    return db.query(models.User).filter(
        models.User.username == username,
        models.User.password == password
    ).first()
