import pandas as pd

# Load main job listings CSV file
main_csv_path = 'backend/simplyhired/simplyhired_jobs.csv'
main_df = pd.read_csv(main_csv_path)

# Load detailed job information CSV file
detailed_csv_path = 'backend/simplyhired/simplyhired_jobs_detailed.csv'
detailed_df = pd.read_csv(detailed_csv_path)

# Standardize column names to lowercase
main_df.columns = main_df.columns.str.lower()
detailed_df.columns = detailed_df.columns.str.lower()

# Print column names for debugging
print("Main DataFrame columns:", main_df.columns)
print("Detailed DataFrame columns:", detailed_df.columns)

# Merge the DataFrames on the 'url' column
merged_df = pd.merge(main_df, detailed_df, on='url', how='left')

# Drop the duplicate columns with _x suffixes
merged_df.drop(columns=['title_x', 'company_x', 'location_x'], inplace=True)

# Rename the remaining columns to remove the _y suffixes
merged_df.rename(columns={
    'title_y': 'title',
    'company_y': 'company',
    'location_y': 'location'
}, inplace=True)

# Fill missing values in the 'posted date' column with 'N/A'
merged_df['posted date'] = merged_df['posted date'].fillna('N/A')

# Save the merged DataFrame to a new CSV file
merged_csv_path = 'backend/simplyhired/simplyhired_combined.csv'
merged_df.to_csv(merged_csv_path, index=False)

print(f"Successfully merged the files and saved to {merged_csv_path}")
