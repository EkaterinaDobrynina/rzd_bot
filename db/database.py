from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
DATABASE_URL = 'sqlite:///example.db'
 
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20, echo=True)
Session = sessionmaker(bind=engine)