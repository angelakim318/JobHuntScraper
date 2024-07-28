from flask import Flask, request, jsonify
import pandas as pd
import subprocess
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Enable CORS for all /api/* routes

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    try:
        # print("Received request for /api/jobs")  
        base_path = os.path.abspath(os.path.dirname(__file__))
        csv_path = os.path.join(base_path, '../data/final_combined_jobs.csv')
        # print(f"CSV Path: {csv_path}")
        
        if os.path.exists(csv_path):
            # print("CSV file found")  
            df = pd.read_csv(csv_path)
            # print(f"CSV Loaded: {df.head()}")  
            return jsonify(df.to_dict(orient='records'))
        else:
            # print("CSV file not found")  
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/jobs/search', methods=['GET'])
def search_jobs():
    try:
        # print("Received request for /api/jobs/search")  
        query = request.args.get('query')
        base_path = os.path.abspath(os.path.dirname(__file__))
        csv_path = os.path.join(base_path, '../data/final_combined_jobs.csv')
        # print(f"CSV Path: {csv_path}")
        
        if os.path.exists(csv_path):
            # print("CSV file found")  
            df = pd.read_csv(csv_path)
            results = df[df['title'].str.contains(query, case=False, na=False)]
            # print(f"Search Results: {results.head()}")  
            return jsonify(results.to_dict(orient='records'))
        else:
            # print("CSV file not found")  
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/scrape', methods=['POST'])
def scrape():
    try:
        # print("Received request for /api/scrape")  
        base_path = os.path.abspath(os.path.dirname(__file__))
        
        # Run Remote.co scripts
        print("Starting Remote.co scraping...")
        result = subprocess.run(["python3", os.path.join(base_path, "../scrapers/remoteco_scraper.py")], capture_output=True, text=True)
        # print(f"Remote.co scraper output: {result.stdout}")
        # print(f"Remote.co scraper error: {result.stderr}")
        
        result = subprocess.run(["python3", os.path.join(base_path, "../scrapers/remoteco_details.py")], capture_output=True, text=True)
        # print(f"Remote.co details output: {result.stdout}")
        # print(f"Remote.co details error: {result.stderr}")
        
        result = subprocess.run(["python3", os.path.join(base_path, "../merge/remoteco_merge.py")], capture_output=True, text=True)
        # print(f"Remote.co merge output: {result.stdout}")
        # print(f"Remote.co merge error: {result.stderr}")
        
        # Repeat for StackOverflow scraper
        print("Starting StackOverflow scraping...")
        result = subprocess.run(["python3", os.path.join(base_path, "../scrapers/stackoverflow_scraper.py")], capture_output=True, text=True)
        # print(f"StackOverflow scraper output: {result.stdout}")
        # print(f"StackOverflow scraper error: {result.stderr}")
        
        result = subprocess.run(["python3", os.path.join(base_path, "../scrapers/stackoverflow_details.py")], capture_output=True, text=True)
        # print(f"StackOverflow details output: {result.stdout}")
        # print(f"StackOverflow details error: {result.stderr}")
        
        result = subprocess.run(["python3", os.path.join(base_path, "../merge/stackoverflow_merge.py")], capture_output=True, text=True)
        # print(f"StackOverflow merge output: {result.stdout}")
        # print(f"StackOverflow merge error: {result.stderr}")
        
        # Repeat for SimplyHired scraper
        print("Starting SimplyHired scraping...")
        result = subprocess.run(["python3", os.path.join(base_path, "../scrapers/simplyhired_scraper.py")], capture_output=True, text=True)
        # print(f"SimplyHired scraper output: {result.stdout}")
        # print(f"SimplyHired scraper error: {result.stderr}")
        
        result = subprocess.run(["python3", os.path.join(base_path, "../scrapers/simplyhired_details.py")], capture_output=True, text=True)
        # print(f"SimplyHired details output: {result.stdout}")
        # print(f"SimplyHired details error: {result.stderr}")
        
        result = subprocess.run(["python3", os.path.join(base_path, "../merge/simplyhired_merge.py")], capture_output=True, text=True)
        # print(f"SimplyHired merge output: {result.stdout}")
        # print(f"SimplyHired merge error: {result.stderr}")
        
        # Combine all job data
        print("Combining all job data...")
        result = subprocess.run(["python3", os.path.join(base_path, "../merge/combine_all_jobs.py")], capture_output=True, text=True)
        # print(f"Combine all jobs output: {result.stdout}")
        # print(f"Combine all jobs error: {result.stderr}")
        
        return jsonify({"message": "Scraping completed"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
