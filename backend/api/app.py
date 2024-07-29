from flask import Flask, request, jsonify
import subprocess
import os
from flask_cors import CORS
from flask_socketio import SocketIO, emit 
from models.models import SessionLocal, Job  # Import the database session and Job model

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    session = SessionLocal()
    try:
        jobs = session.query(Job).all()
        # Helper function to convert SQLAlchemy models to dictionaries
        jobs_list = [job.to_dict() for job in jobs]
        # Replace None with 'N/A'
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
def search_jobs():
    session = SessionLocal()
    try:
        query = request.args.get('query')
        jobs = session.query(Job).filter(Job.title.ilike(f'%{query}%')).all()
        jobs_list = [job.to_dict() for job in jobs]
        # Replace None with 'N/A'
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
