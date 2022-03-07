from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataBase import DataBase


def create_connection_db():
    data_base_name = 'application.sqlite'
    engine = create_engine(f'sqlite:///{data_base_name}')
    session = sessionmaker(bind=engine)
    s = session()
    return s


def insert_line_db(s, filename, frame_n, time, rle):
    video = DataBase(video_name=filename, frame_number=frame_n, time_stamp=time, rle=rle) 
    s.add(video) 
    s.commit()
