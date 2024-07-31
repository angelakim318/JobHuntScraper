from flask import Flask, request, jsonify
import subprocess
import os
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from models.models import SessionLocal, Job, User, DATABASE_URL
from sqlalchemy.exc import SQLAlchemyError
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Load secret key from .env

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
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200
        return jsonify({"msg": "Invalid username or password"}), 401
    except SQLAlchemyError as e:
        return jsonify({"msg": str(e)}), 500
    finally:
        session.close()

@app.route('/api/jobs', methods=['GET'])
@jwt_required()
def get_jobs():
    session = SessionLocal()
    try:
        print("Fetching jobs from database")
        jobs = session.query(Job).all()
        jobs_list = [job.to_dict() for job in jobs]
        for job in jobs_list:
            for key, value in job.items():
                if value is None:
                    job[key] = 'N/A'
        print(f"Jobs fetched: {jobs_list}")
        return jsonify(jobs_list)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/api/jobs/search', methods=['GET'])
@jwt_required()
def search_jobs():
    session = SessionLocal()
    try:
        query = request.args.get('query')
        jobs = session.query(Job).filter(Job.title.ilike(f'%{query}%')).all()
        jobs_list = [job.to_dict() for job in jobs]
        for job in jobs_list:
            for key, value in job.items():
                if value is None:
                    job[key] = 'N/A'
        return jsonify(jobs_list)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/api/scrape', methods=['POST'])
@jwt_required()
def scrape():
    try:
        base_path = os.path.abspath(os.path.dirname(__file__))
        
        socketio.emit('scrape_progress', {'message': 'Scraping has started'})

        tasks = [
            {"name": "Remote.co scraping", "script": "../scrapers/remoteco_scraper.py"},
            {"name": "Remote.co details", "script": "../scrapers/remoteco_details.py"},
            {"name": "Remote.co merge", "script": "../merge/remoteco_merge.py"},
            {"name": "StackOverflow scraping", "script": "../scrapers/stackoverflow_scraper.py"},
            {"name": "StackOverflow details", "script": "../scrapers/stackoverflow_details.py"},
            {"name": "StackOverflow merge", "script": "../merge/stackoverflow_merge.py"},
            {"name": "SimplyHired scraping", "script": "../scrapers/simplyhired_scraper.py"},
            {"name": "SimplyHired details", "script": "../scrapers/simplyhired_details.py"},
            {"name": "SimplyHired merge", "script": "../merge/simplyhired_merge.py"},
        ]

        for task in tasks:
            result = subprocess.run(["python3", os.path.join(base_path, task["script"])], capture_output=True, text=True)
            if result.returncode != 0:
                socketio.emit('scrape_progress', {'message': f'Error in {task["name"]}: {result.stderr}'})
            else:
                socketio.emit('scrape_progress', {'message': f'{task["name"]} completed'})

        socketio.emit('scrape_progress', {'message': 'Combining all job data'})
        
        # Combining all job data
        script_dir = os.path.dirname(os.path.abspath(__file__))
        remoteco_combined_path = os.path.join(script_dir, '..', 'data', 'remoteco_combined.csv')
        simplyhired_combined_path = os.path.join(script_dir, '..', 'data', 'simplyhired_combined.csv')
        stackoverflow_combined_path = os.path.join(script_dir, '..', 'data', 'stackoverflow_combined.csv')
        final_combined_csv_path = os.path.join(script_dir, '..', 'data', 'final_combined_jobs.csv')

        print("Loading CSV files into DataFrames...")
        remoteco_df = pd.read_csv(remoteco_combined_path)
        simplyhired_df = pd.read_csv(simplyhired_combined_path)
        stackoverflow_df = pd.read_csv(stackoverflow_combined_path)

        print("Concatenating DataFrames...")
        final_combined_df = pd.concat([remoteco_df, simplyhired_df, stackoverflow_df], ignore_index=True, sort=False)

        final_combined_df.fillna('N/A', inplace=True)

        final_combined_df['qualifications'] = final_combined_df['qualifications'].apply(lambda x: ', '.join(eval(x)) if isinstance(x, str) and x.startswith('[') else x)

        os.makedirs(os.path.dirname(final_combined_csv_path), exist_ok=True)

        print("Saving final combined DataFrame to CSV...")
        final_combined_df.to_csv(final_combined_csv_path, index=False)

        socketio.emit('scrape_progress', {'message': 'Loading data into the database'})

        print("Connecting to database and loading data...")
        engine = create_engine(DATABASE_URL)
        session = SessionLocal()
        
        try:
            print("Clearing existing job data...")
            session.query(Job).delete()
            session.commit()

            print("Inserting new job data...")
            jobs_data = final_combined_df.to_dict(orient='records')

            for job_data in jobs_data:
                job = Job(
                    url=job_data['url'] if job_data['url'] != 'N/A' else None,
                    title=job_data['title'] if job_data['title'] != 'N/A' else None,
                    company=job_data['company'] if job_data['company'] != 'N/A' else None,
                    job_type=job_data['job type'] if job_data['job type'] != 'N/A' else None,
                    location=job_data['location'] if job_data['location'] != 'N/A' else None,
                    benefits=job_data['benefits'] if job_data['benefits'] != 'N/A' else None,
                    posted_date=pd.to_datetime(job_data['posted date'], errors='coerce') if job_data['posted date'] != 'N/A' else None,
                    qualifications=job_data['qualifications'] if job_data['qualifications'] != 'N/A' else None,
                    job_description=job_data['job description'].replace('\n', '<br>') if job_data['job description'] != 'N/A' else None
                )

                if job.posted_date and pd.isna(job.posted_date):
                    job.posted_date = None

                session.add(job)
            
            session.commit()
            print("New data inserted into the jobs table")
            socketio.emit('scrape_progress', {'message': 'Data loading completed'})

        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error occurred: {e}")
            socketio.emit('scrape_progress', {'message': f'Error loading data into database: {e}'})
        finally:
            session.close()
            print("Database session closed")

        socketio.emit('scrape_complete')
        return jsonify({"message": "Scraping completed"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True)
