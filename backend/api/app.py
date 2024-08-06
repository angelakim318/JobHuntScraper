from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from backend.models.models import SessionLocal, Job, User, ScrapeStatus, DATABASE_URL, init_db
from sqlalchemy.exc import SQLAlchemyError
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from datetime import timedelta
import os
import pandas as pd
import subprocess
from sqlalchemy import create_engine

# Load environment variables from .env 
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize the database
init_db()

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
    session = SessionLocal()
    try:
        scrape_status = session.query(ScrapeStatus).filter_by(source='remoteco').first()
        if scrape_status and scrape_status.scraped:
            return jsonify({"message": "Remote.co has already been scraped"}), 400

        result = run_scraper(user_id, "remoteco", [
            "../scrapers/remoteco_scraper.py",
            "../scrapers/remoteco_details.py",
            "../merge/remoteco_merge.py"
        ])

        if scrape_status:
            scrape_status.scraped = True
        else:
            scrape_status = ScrapeStatus(source='remoteco', scraped=True)
            session.add(scrape_status)

        session.commit()
        socketio.emit('scrape_complete', {'source': 'remoteco'})
        return jsonify({"message": "remoteco scraping completed"}), 202
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/api/scrape/stackoverflow', methods=['POST'])
@jwt_required()
def scrape_stackoverflow():
    user_id = get_jwt_identity()
    session = SessionLocal()
    try:
        scrape_status = session.query(ScrapeStatus).filter_by(source='stackoverflow').first()
        if scrape_status and scrape_status.scraped:
            return jsonify({"message": "StackOverflow has already been scraped"}), 400

        result = run_scraper(user_id, "stackoverflow", [
            "../scrapers/stackoverflow_scraper.py",
            "../scrapers/stackoverflow_details.py",
            "../merge/stackoverflow_merge.py"
        ])

        if scrape_status:
            scrape_status.scraped = True
        else:
            scrape_status = ScrapeStatus(source='stackoverflow', scraped=True)
            session.add(scrape_status)

        session.commit()
        socketio.emit('scrape_complete', {'source': 'stackoverflow'})
        return jsonify({"message": "stackoverflow scraping completed"}), 202
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/api/scrape/simplyhired', methods=['POST'])
@jwt_required()
def scrape_simplyhired():
    user_id = get_jwt_identity()
    session = SessionLocal()
    try:
        scrape_status = session.query(ScrapeStatus).filter_by(source='simplyhired').first()
        if scrape_status and scrape_status.scraped:
            return jsonify({"message": "SimplyHired has already been scraped"}), 400

        result = run_scraper(user_id, "simplyhired", [
            "../scrapers/simplyhired_scraper.py",
            "../scrapers/simplyhired_details.py",
            "../merge/simplyhired_merge.py"
        ])

        if scrape_status:
            scrape_status.scraped = True
        else:
            scrape_status = ScrapeStatus(source='simplyhired', scraped=True)
            session.add(scrape_status)

        session.commit()
        socketio.emit('scrape_complete', {'source': 'simplyhired'})
        return jsonify({"message": "simplyhired scraping completed"}), 202
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/api/clear_database', methods=['POST'])
@jwt_required()
def clear_database():
    user_id = get_jwt_identity()
    try:
        session = SessionLocal()
        session.query(Job).filter_by(user_id=user_id).delete()
        session.query(ScrapeStatus).delete()
        session.commit()
        return jsonify({"message": "Database cleared successfully"}), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/scrape/status', methods=['GET'])
@jwt_required()
def scrape_status():
    session = SessionLocal()
    try:
        status = {status.source: status.scraped for status in session.query(ScrapeStatus).all()}
        return jsonify(status)
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

def run_scraper(user_id, source_name, scripts):
    base_path = os.path.abspath(os.path.dirname(__file__))

    for script in scripts:
        result = subprocess.run(["python3", os.path.join(base_path, script)], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error in {source_name} scraping: {result.stderr}")
            return f"Error in {source_name} scraping: {result.stderr}"
        else:
            print(f"{source_name} scraping completed successfully.")

    # Load combined data into database
    csv_file_name = f'{source_name}_combined.csv'
    combined_csv_path = os.path.join(base_path, '..', 'data', csv_file_name)

    if not os.path.exists(combined_csv_path):
        return f'CSV file {combined_csv_path} was not found.'

    combined_df = pd.read_csv(combined_csv_path)
    combined_df.fillna('N/A', inplace=True)  # Fill NA values with 'N/A'

    if 'qualifications' in combined_df.columns:
        combined_df['qualifications'] = combined_df['qualifications'].apply(lambda x: ', '.join(eval(x)) if isinstance(x, str) and x.startswith('[') else x)

    engine = create_engine(DATABASE_URL)
    session = SessionLocal()

    try:
        for _, job_data in combined_df.iterrows():
            job = Job(
                url=job_data['url'] if job_data['url'] != 'N/A' else None,
                title=job_data['title'] if job_data['title'] != 'N/A' else 'No Title',
                company=job_data['company'] if job_data['company'] != 'N/A' else None,
                job_type=job_data.get('job type', 'N/A') if job_data.get('job type', 'N/A') != 'N/A' else None,
                location=job_data['location'] if job_data['location'] != 'N/A' else None,
                benefits=job_data.get('benefits', 'N/A') if job_data.get('benefits', 'N/A') != 'N/A' else None,
                posted_date=job_data.get('posted date', 'N/A'),  # Store as string
                qualifications=job_data.get('qualifications', 'N/A') if 'qualifications' in job_data and job_data['qualifications'] != 'N/A' else None,
                job_description=job_data['job description'].replace('\n', '<br>') if 'job description' in job_data and job_data['job description'] != 'N/A' else None,
                user_id=user_id
            )

            session.add(job)

        session.commit()
        return f'{source_name} scraping completed'
    except SQLAlchemyError as e:
        session.rollback()
        return f'Error loading {source_name} data into database: {e}'
    finally:
        session.close()

if __name__ == '__main__':
    socketio.run(app, debug=True)
