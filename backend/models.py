from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)
    full_name = Column(String)
    age = Column(Integer)
    role = Column(String)
    profile_photo = Column(String)

    lat = Column(String, default="")
    lng = Column(String, default="")
    status = Column(String, default="INACTIVE")
