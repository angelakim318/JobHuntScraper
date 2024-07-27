import pandas as pd

def merge_stackoverflow_files(main_csv_path='backend/data/stackoverflow_jobs.csv', detailed_csv_path='backend/data/stackoverflow_jobs_detailed.csv', merged_csv_path='backend/data/stackoverflow_combined.csv'):
    # Load main job listings CSV file
    main_df = pd.read_csv(main_csv_path)

    # Load detailed job information CSV file
    detailed_df = pd.read_csv(detailed_csv_path)

    # Set column names to lowercase
    main_df.columns = main_df.columns.str.lower()
    detailed_df.columns = detailed_df.columns.str.lower()

    # Merge DataFrames on 'url' column
    merged_df = pd.merge(main_df, detailed_df, on='url', how='left')

    # Drop duplicate columns with _x suffixes
    merged_df.drop(columns=['title_x', 'company_x', 'location_x'], inplace=True)

    # Rename remaining columns to remove _y suffixes
    merged_df.rename(columns={
        'title_y': 'title',
        'company_y': 'company',
        'location_y': 'location'
    }, inplace=True)

    # Fill missing values with 'N/A'
    merged_df.fillna('N/A', inplace=True)

    # Save merged DataFrame to a new CSV file
    merged_df.to_csv(merged_csv_path, index=False)

    print(f"Successfully merged the files and saved to {merged_csv_path}")

# If script is run directly, call the function
if __name__ == '__main__':
    merge_stackoverflow_files()