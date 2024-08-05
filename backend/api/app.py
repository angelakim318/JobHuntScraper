from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from backend.models.models import SessionLocal, Job, User, DATABASE_URL
from sqlalchemy.exc import SQLAlchemyError
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from datetime import timedelta
import os
import pandas as pd
import subprocess
from sqlalchemy import create_engine
from celery import Celery

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    first_name = data.get('first_name')
    username = data.get('username')
    password = data.get('password')

    if not first_name or not username or not password:
        return jsonify({"msg": "Missing first name, username or password"}), 400

    session = SessionLocal()
    try:
        user = User(first_name=first_name, username=username)
        user.set_password(password)
        session.add(user)
        session.commit()
        return jsonify({"msg": "User registered successfully"}), 201
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"msg": str(e)}), 500
    finally:
        session.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id)
            response = jsonify(access_token=access_token)
            return response, 200
        return jsonify({"msg": "Invalid username or password"}), 401
    except SQLAlchemyError as e:
        return jsonify({"msg": str(e)}), 500
    finally:
        session.close()

@app.route('/api/jobs', methods=['GET'])
@jwt_required()
def get_jobs():
    user_id = get_jwt_identity()
    session = SessionLocal()
    try:
        jobs = session.query(Job).filter_by(user_id=user_id).all()
        jobs_list = [job.to_dict() for job in jobs]
        for job in jobs_list:
            for key, value in job.items():
                if value is None:
                    job[key] = 'N/A'
        return jsonify(jobs_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/api/jobs/search', methods=['GET'])
@jwt_required()
def search_jobs():
    user_id = get_jwt_identity()
    session = SessionLocal()
    try:
        query = request.args.get('query')
        jobs = session.query(Job).filter(Job.title.ilike(f'%{query}%'), Job.user_id == user_id).all()
        jobs_list = [job.to_dict() for job in jobs]
        for job in jobs_list:
            for key, value in job.items():
                if value is None:
                    job[key] = 'N/A'
        return jsonify(jobs_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/api/scrape/remoteco', methods=['POST'])
@jwt_required()
def scrape_remoteco():
    user_id = get_jwt_identity()
    scrape_remoteco_jobs.delay(user_id)
    return jsonify({"message": "Remote.co scraping has started"}), 202

@app.route('/api/scrape/stackoverflow', methods=['POST'])
@jwt_required()
def scrape_stackoverflow():
    user_id = get_jwt_identity()
    scrape_stackoverflow_jobs.delay(user_id)
    return jsonify({"message": "StackOverflow scraping has started"}), 202

@app.route('/api/scrape/simplyhired', methods=['POST'])
@jwt_required()
def scrape_simplyhired():
    user_id = get_jwt_identity()
    scrape_simplyhired_jobs.delay(user_id)
    return jsonify({"message": "SimplyHired scraping has started"}), 202

@app.route('/api/clear_database', methods=['POST'])
@jwt_required()
def clear_database():
    user_id = get_jwt_identity()
    try:
        session = SessionLocal()
        session.query(Job).filter_by(user_id=user_id).delete()
        session.commit()
        return jsonify({"message": "Database cleared successfully"}), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

# Celery tasks for scraping
@celery.task
def scrape_remoteco_jobs(user_id):
    run_scraper(user_id, "Remote.co", [
        "../scrapers/remoteco_scraper.py",
        "../scrapers/remoteco_details.py",
        "../merge/remoteco_merge.py"
    ])

@celery.task
def scrape_stackoverflow_jobs(user_id):
    run_scraper(user_id, "StackOverflow", [
        "../scrapers/stackoverflow_scraper.py",
        "../scrapers/stackoverflow_details.py",
        "../merge/stackoverflow_merge.py"
    ])

@celery.task
def scrape_simplyhired_jobs(user_id):
    run_scraper(user_id, "SimplyHired", [
        "../scrapers/simplyhired_scraper.py",
        "../scrapers/simplyhired_details.py",
        "../merge/simplyhired_merge.py"
    ])

def run_scraper(user_id, source_name, scripts):
    base_path = os.path.abspath(os.path.dirname(__file__))

    for script in scripts:
        result = subprocess.run(["python3", os.path.join(base_path, script)], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error in {source_name} scraping: {result.stderr}")
        else:
            print(f"{source_name} scraping completed successfully.")

    # Load combined data into database
    emit('scrape_progress', {'message': f'Loading {source_name} data into the database'})

    combined_csv_path = os.path.join(base_path, f'../data/{source_name.lower()}_combined.csv')
    combined_df = pd.read_csv(combined_csv_path)
    combined_df.fillna('N/A', inplace=True)
    combined_df['qualifications'] = combined_df['qualifications'].apply(lambda x: ', '.join(eval(x)) if isinstance(x, str) and x.startswith('[') else x)

    engine = create_engine(DATABASE_URL)
    session = SessionLocal()

    try:
        for _, job_data in combined_df.iterrows():
            job_description = job_data.get('job_description', 'N/A')
            job = Job(
                url=job_data['url'] if job_data['url'] != 'N/A' else None,
                title=job_data['title'] if job_data['title'] != 'N/A' else None,
                company=job_data['company'] if job_data['company'] != 'N/A' else None,
                job_type=job_data['job type'] if job_data['job type'] != 'N/A' else None,
                location=job_data['location'] if job_data['location'] != 'N/A' else None,
                benefits=job_data['benefits'] if job_data['benefits'] != 'N/A' else None,
                posted_date=pd.to_datetime(job_data['posted date'], errors='coerce') if job_data['posted date'] != 'N/A' else None,
                qualifications=job_data['qualifications'] if job_data['qualifications'] != 'N/A' else None,
                job_description=job_description.replace('\n', '<br>') if job_description != 'N/A' else None,
                user_id=user_id
            )

            if job.posted_date and pd.isna(job.posted_date):
                job.posted_date = None

            session.add(job)

        session.commit()
        emit('scrape_progress', {'message': f'{source_name} data loading completed'})

    except SQLAlchemyError as e:
        session.rollback()
        emit('scrape_progress', {'message': f'Error loading {source_name} data into database: {e}'})
    finally:
        session.close()

    emit('scrape_complete')

if __name__ == '__main__':
    socketio.run(app, debug=True)
