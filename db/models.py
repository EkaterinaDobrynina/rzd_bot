from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
 
Base = declarative_base()
 
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    telegram_id  = Column(String, index=True, nullable=False, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)


class Questionnaire(Base):
    __tablename__ = 'questionnaire'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, nullable=False)
    answer = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
 
    user = relationship('User', back_populates='questionnaire')
 
User.questionnaire = relationship('Questionnaire', order_by=Questionnaire.id, back_populates='user')