import pandas as pd
import os

def combine_all_jobs():
    # Get the absolute path of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full paths to the CSV files relative to the project's root
    remoteco_combined_path = os.path.join(script_dir, '..', 'data', 'remoteco_combined.csv')
    simplyhired_combined_path = os.path.join(script_dir, '..', 'data', 'simplyhired_combined.csv')
    stackoverflow_combined_path = os.path.join(script_dir, '..', 'data', 'stackoverflow_combined.csv')
    final_combined_csv_path = os.path.join(script_dir, '..', 'data', 'final_combined_jobs.csv')

    print(f"Running combine script in {os.getcwd()}")
    
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

    print(f"Successfully combined all job listings into {final_combined_csv_path}")

# If script is run directly, call the function
if __name__ == '__main__':
    combine_all_jobs()