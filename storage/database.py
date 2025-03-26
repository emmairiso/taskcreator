from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker
#from models.base import Base
#from models.account import Account
#from models.task import Task

#engine = create_engine("sqlite:///tasks.db", echo=False)
#Session = sessionmaker(bind=engine)
#session = Session()

#Base.metadata.create_all(engine) 

db = SQLAlchemy()
