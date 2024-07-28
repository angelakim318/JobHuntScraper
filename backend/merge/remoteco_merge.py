import pandas as pd
import os 

def merge_remoteco_files():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_csv_path = os.path.join(script_dir, '..', 'data', 'remoteco_jobs.csv')
    detailed_csv_path = os.path.join(script_dir, '..', 'data', 'remoteco_jobs_detailed.csv')
    merged_csv_path = os.path.join(script_dir, '..', 'data', 'remoteco_combined.csv')

    print(f"Running remoteco script in {os.getcwd()}")
    
    # Load main job listings CSV file
    main_df = pd.read_csv(main_csv_path)

    # Load detailed job information CSV file
    detailed_df = pd.read_csv(detailed_csv_path)

    # Set column names to lowercase
    main_df.columns = main_df.columns.str.lower()
    detailed_df.columns = detailed_df.columns.str.lower()

    # Merge DataFrames on the 'url' column
    merged_df = pd.merge(main_df, detailed_df, on='url', how='left')

    # Drop duplicate columns with _x suffixes
    merged_df.drop(columns=['title_x', 'company_x', 'job type_x'], inplace=True)

    # Rename remaining columns to remove _y suffixes
    merged_df.rename(columns={
        'title_y': 'title',
        'company_y': 'company',
        'job type_y': 'job type'
    }, inplace=True)

    # Fill missing values with 'N/A'
    merged_df.fillna('N/A', inplace=True)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(merged_csv_path), exist_ok=True)

    # Save merged DataFrame to a new CSV file
    merged_df.to_csv(merged_csv_path, index=False)

    print(f"Successfully merged the files and saved to {merged_csv_path}")

# If script is run directly, call the function
if __name__ == '__main__':
    merge_remoteco_files()