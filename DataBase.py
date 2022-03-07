from sqlalchemy import Column, Integer, String  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy import create_engine


DATABASE_NAME = 'application.sqlite'

engine = create_engine(f'sqlite:///{DATABASE_NAME}')
Base = declarative_base() 


class DataBase(Base):  
    __tablename__ = 'Videos'  
    id_video = Column(Integer, primary_key=True)  
    video_name = Column(String(250), nullable=False)
    frame_number = Column(Integer, nullable=False)
    time_stamp = Column(String(250), nullable=False)
    rle = Column(String(250), nullable=False)


Base.metadata.create_all(engine)
