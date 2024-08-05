import pandas as pd
import os
from concurrent.futures import ProcessPoolExecutor
from sqlalchemy import create_engine
from models.models import Job, DATABASE_URL, SessionLocal
from sqlalchemy.exc import SQLAlchemyError

def load_csv(file_path):
    return pd.read_csv(file_path)

def merge_csv(file_paths):
    with ProcessPoolExecutor() as executor:
        dfs = list(executor.map(load_csv, file_paths))
    return pd.concat(dfs, ignore_index=True)

def combine_all_jobs():
    # Check if data already exists in the database
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    if session.query(Job).first():
        print("Data already exists in the database. Skipping combining jobs.")
        session.close()
        return
    session.close()

    # Get the absolute path of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("Script directory:", script_dir)
    
    # Construct the full paths to the CSV files relative to the project's root
    remoteco_combined_path = os.path.join(script_dir, '..', 'data', 'remoteco_combined.csv')
    simplyhired_combined_path = os.path.join(script_dir, '..', 'data', 'simplyhired_combined.csv')
    stackoverflow_combined_path = os.path.join(script_dir, '..', 'data', 'stackoverflow_combined.csv')
    final_combined_csv_path = os.path.join(script_dir, '..', 'data', 'final_combined_jobs.csv')
    
    file_paths = [remoteco_combined_path, simplyhired_combined_path, stackoverflow_combined_path]

    # Load and merge each CSV file into a DataFrame concurrently
    print("Loading and merging CSV files into DataFrames concurrently...")
    final_combined_df = merge_csv(file_paths)

    # Replace NaN values with 'N/A'
    final_combined_df.fillna('N/A', inplace=True)

    # Convert list-like qualifications to a comma-separated string
    final_combined_df['qualifications'] = final_combined_df['qualifications'].apply(lambda x: ', '.join(eval(x)) if isinstance(x, str) and x.startswith('[') else x)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(final_combined_csv_path), exist_ok=True)

    # Save final combined DataFrame to a new CSV file
    print("Saving final combined DataFrame to CSV...")
    final_combined_df.to_csv(final_combined_csv_path, index=False)

    # Load data into PostgreSQL database
    print("Connecting to database and loading data...")
    engine = create_engine(DATABASE_URL)
    session = SessionLocal()
    
    try:
        # Clear existing data
        print("Clearing existing job data...")
        session.query(Job).delete()
        session.commit()

        # Insert new data
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
                job_description=job_data['job description'].replace('\n', '<br>') if job_data['job_description'] != 'N/A' else None
            )
            
            # Ensure posted_date is None if it is NaT
            if job.posted_date and pd.isna(job.posted_date):
                job.posted_date = None

            session.add(job)
        
        session.commit()
        print("New data inserted into the jobs table")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error occurred: {e}")
    finally:
        session.close()
        print("Database session closed")

if __name__ == '__main__':
    combine_all_jobs()
    print("Scraping and data insertion completed.")
