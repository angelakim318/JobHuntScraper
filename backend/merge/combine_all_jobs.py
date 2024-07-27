import pandas as pd

def combine_all_jobs(remoteco_combined_path='backend/data/remoteco_combined.csv', simplyhired_combined_path='backend/data/simplyhired_combined.csv', stackoverflow_combined_path='backend/data/stackoverflow_combined.csv', final_combined_csv_path='backend/data/final_combined_jobs.csv'):
    # Load each combined CSV file into a DataFrame
    remoteco_df = pd.read_csv(remoteco_combined_path)
    simplyhired_df = pd.read_csv(simplyhired_combined_path)
    stackoverflow_df = pd.read_csv(stackoverflow_combined_path)

    # Concatenate all DataFrames
    final_combined_df = pd.concat([remoteco_df, simplyhired_df, stackoverflow_df], ignore_index=True, sort=False)

    # Replace NaN values with 'N/A'
    final_combined_df.fillna('N/A', inplace=True)

    # Save final combined DataFrame to a new CSV file
    final_combined_df.to_csv(final_combined_csv_path, index=False)

    print(f"Successfully combined all job listings into {final_combined_csv_path}")

# If script is run directly, call the function
if __name__ == '__main__':
    combine_all_jobs()