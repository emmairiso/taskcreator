from storage.database import db
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship



class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False, unique=True)
    tasks = relationship('Task', back_populates='user', cascade = "all, delete-orphan")
