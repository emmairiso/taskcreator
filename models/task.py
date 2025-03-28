from storage.database import db
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    due_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship('User', back_populates='tasks')

    def is_overdue(self):
        return self.due_date < date.today()