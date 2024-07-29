# models/models.py

from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    job_type = Column(String, nullable=True)
    location = Column(String, nullable=True)
    benefits = Column(String, nullable=True)
    posted_date = Column(Date, nullable=True)
    qualifications = Column(String, nullable=True)
    job_description = Column(String, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'company': self.company,
            'job_type': self.job_type,
            'location': self.location,
            'benefits': self.benefits,
            'posted_date': self.posted_date,
            'qualifications': self.qualifications,
            'job_description': self.job_description,
        }

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

DATABASE_URL = 'postgresql+psycopg2://angelakim:angelakim123@localhost/job_scraping_db'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
