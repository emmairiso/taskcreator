from storage.database import db
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin



class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    verified = db.Column(db.Boolean, default=False)
    tasks = relationship('Task', back_populates='user', cascade = "all, delete-orphan")

def create_user(email, password):
    new_user = User(email=email, password=password)
    db.session.add(new_user)
