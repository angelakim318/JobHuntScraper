from flask import Flask, request, jsonify
import pandas as pd
import subprocess

app = Flask(__name__)

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    df = pd.read_csv('../data/final_combined_jobs.csv')
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/jobs/search', methods=['GET'])
def search_jobs():
    query = request.args.get('query')
    df = pd.read_csv('../data/final_combined_jobs.csv')
    results = df[df['Title'].str.contains(query, case=False, na=False)]
    return jsonify(results.to_dict(orient='records'))

@app.route('/api/scrape', methods=['POST'])
def scrape():
    # Run Remote.co scripts
    subprocess.call(["python", "../scrapers/remoteco_scraper.py"])
    subprocess.call(["python", "../scrapers/remoteco_details.py"])
    subprocess.call(["python", "../merge/remoteco_merge.py"])

    # Run SimplyHired scripts
    subprocess.call(["python", "../scrapers/simplyhired_scraper.py"])
    subprocess.call(["python", "../scrapers/simplyhired_details.py"])
    subprocess.call(["python", "../merge/simplyhired_merge.py"])

    # Run StackOverflow scripts
    subprocess.call(["python", "../scrapers/stackoverflow_scraper.py"])
    subprocess.call(["python", "../scrapers/stackoverflow_details.py"])
    subprocess.call(["python", "../merge/stackoverflow_merge.py"])

    # Combine all merged CSV files
    subprocess.call(["python", "../merge/combine_all_jobs.py"])

    return jsonify({"message": "Scraping started"}), 202

if __name__ == '__main__':
    app.run(debug=True)
