import pandas as pd

# Paths to the combined CSV files
remoteco_combined_path = 'backend/remoteco/remoteco_combined.csv'
simplyhired_combined_path = 'backend/simplyhired/simplyhired_combined.csv'
stackoverflow_combined_path = 'backend/stackoverflow_jobs/stackoverflow_combined.csv'

# Load each combined CSV file into a DataFrame
remoteco_df = pd.read_csv(remoteco_combined_path)
simplyhired_df = pd.read_csv(simplyhired_combined_path)
stackoverflow_df = pd.read_csv(stackoverflow_combined_path)

# Concatenate the DataFrames
final_combined_df = pd.concat([remoteco_df, simplyhired_df, stackoverflow_df], ignore_index=True, sort=False)

# Replace NaN values with 'N/A'
final_combined_df.fillna('N/A', inplace=True)

# Save the final combined DataFrame to a new CSV file
final_combined_csv_path = 'backend/final_combined_jobs.csv'
final_combined_df.to_csv(final_combined_csv_path, index=False)

print(f"Successfully combined all job listings into {final_combined_csv_path}")
