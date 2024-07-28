import pandas as pd
import os
from sqlalchemy import create_engine
from models.models import Job, DATABASE_URL, SessionLocal

def combine_all_jobs():
    # Get the absolute path of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full paths to the CSV files relative to the project's root
    remoteco_combined_path = os.path.join(script_dir, '..', 'data', 'remoteco_combined.csv')
    simplyhired_combined_path = os.path.join(script_dir, '..', 'data', 'simplyhired_combined.csv')
    stackoverflow_combined_path = os.path.join(script_dir, '..', 'data', 'stackoverflow_combined.csv')
    final_combined_csv_path = os.path.join(script_dir, '..', 'data', 'final_combined_jobs.csv')
    # print(f"Running combine script in {os.getcwd()}")
    
    # Load each combined CSV file into a DataFrame
    remoteco_df = pd.read_csv(remoteco_combined_path)
    simplyhired_df = pd.read_csv(simplyhired_combined_path)
    stackoverflow_df = pd.read_csv(stackoverflow_combined_path)

    # Concatenate all DataFrames
    final_combined_df = pd.concat([remoteco_df, simplyhired_df, stackoverflow_df], ignore_index=True, sort=False)

    # Replace NaN values with 'N/A'
    final_combined_df.fillna('N/A', inplace=True)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(final_combined_csv_path), exist_ok=True)

    # Save final combined DataFrame to a new CSV file
    final_combined_df.to_csv(final_combined_csv_path, index=False)

    # print(f"Successfully combined all job listings into {final_combined_csv_path}")

    # Load data into PostgreSQL database
    engine = create_engine(DATABASE_URL)
    session = SessionLocal()
    
    jobs_data = final_combined_df.to_dict(orient='records')

    for job_data in jobs_data:
        # Convert 'N/A' to None for posted_date
        posted_date = pd.to_datetime(job_data['posted date'], errors='coerce')
        job_data['posted date'] = posted_date.date() if not pd.isna(posted_date) else None
        
        job = Job(
            url=job_data['url'],
            title=job_data['title'],
            company=job_data['company'],
            job_type=job_data['job type'],
            location=job_data['location'],
            benefits=job_data['benefits'],
            posted_date=job_data['posted date'],
            qualifications=job_data['qualifications'],
            job_description=job_data['job description']
        )
        session.add(job)
    session.commit()
    session.close()

    # print("Data successfully loaded into the database.")

# If script is run directly, call the function
if __name__ == '__main__':
    combine_all_jobs()