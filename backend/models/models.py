import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables from .env 
load_dotenv()

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
    posted_date = Column(String, nullable=True)  
    qualifications = Column(String, nullable=True)
    job_description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship('User', back_populates='jobs')

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'company': self.company if self.company else 'N/A',
            'job_type': self.job_type if self.job_type and self.job_type.lower() != 'nan' else 'N/A',
            'location': self.location if self.location else 'N/A',
            'benefits': self.benefits if self.benefits else 'N/A',
            'posted_date': self.posted_date if self.posted_date else 'N/A',
            'qualifications': self.qualifications.replace('[', '').replace(']', '').replace('\'', '') if self.qualifications else 'N/A',
            'job_description': self.job_description if self.job_description else 'N/A',
        }

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    jobs = relationship('Job', back_populates='user')
    scrape_statuses = relationship('ScrapeStatus', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class SavedJob(Base):
    __tablename__ = 'saved_jobs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)

    user = relationship('User', back_populates='saved_jobs')
    job = relationship('Job')

# Add a relationship to the User model
User.saved_jobs = relationship('SavedJob', back_populates='user')

class ScrapeStatus(Base):
    __tablename__ = 'scrape_status'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String, nullable=False)
    scraped = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship('User', back_populates='scrape_statuses')

# Load database credentials from environment variables
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

DATABASE_URL = f'postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
