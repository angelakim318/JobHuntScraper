from flask import Flask, request, jsonify
import subprocess
import os
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from models.models import SessionLocal, Job, User
from sqlalchemy.exc import SQLAlchemyError
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv

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
        jobs = session.query(Job).all()
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
            {"name": "Combine all jobs", "script": "../merge/combine_all_jobs.py"},
        ]

        for task in tasks:
            result = subprocess.run(["python3", os.path.join(base_path, task["script"])], capture_output=True, text=True)
            if result.returncode != 0:
                socketio.emit('scrape_progress', {'message': f'Error in {task["name"]}: {result.stderr}'})
            else:
                socketio.emit('scrape_progress', {'message': f'{task["name"]} completed'})

        socketio.emit('scrape_complete')
        return jsonify({"message": "Scraping completed"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True)
