from flask import Flask, request, jsonify
import pandas as pd
import subprocess
import os
from flask_cors import CORS
from flask_socketio import SocketIO, emit 

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    try:
        base_path = os.path.abspath(os.path.dirname(__file__))
        csv_path = os.path.join(base_path, '../data/final_combined_jobs.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df.fillna('N/A', inplace=True)
            return jsonify(df.to_dict(orient='records'))
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/jobs/search', methods=['GET'])
def search_jobs():
    try:
        query = request.args.get('query')
        base_path = os.path.abspath(os.path.dirname(__file__))
        csv_path = os.path.join(base_path, '../data/final_combined_jobs.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df.fillna('N/A', inplace=True)
            results = df[df['title'].str.contains(query, case=False, na=False)]
            return jsonify(results.to_dict(orient='records'))
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

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
            # print(f"Starting {task['name']}...")
            result = subprocess.run(["python3", os.path.join(base_path, task["script"])], capture_output=True, text=True)
            # print(f"{task['name']} output: {result.stdout}")
            # print(f"{task['name']} error: {result.stderr}")
            if result.returncode != 0:
                # print(f"Error in {task['name']}: {result.stderr}")
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