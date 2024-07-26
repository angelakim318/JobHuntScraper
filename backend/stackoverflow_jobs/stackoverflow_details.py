import csv
from selenium import webdriver
from selenium.webdriver.safari.service import Service
from selenium.webdriver.safari.options import Options
import time
from bs4 import BeautifulSoup

# Read existing CSV file
input_csv_file = './backend/stackoverflow_jobs/stackoverflow_jobs.csv'
output_csv_file = './backend/stackoverflow_jobs/stackoverflow_jobs_detailed.csv'

# Define Safari options
safari_options = Options()

# Initialize WebDriver with Safari options
driver = webdriver.Safari(service=Service(), options=safari_options)

# Define columns for CSV
fieldnames = ['Title', 'Company', 'Location', 'URL', 'Job Description']

# Open input CSV file and create output CSV file
with open(input_csv_file, mode='r', newline='') as infile, open(output_csv_file, mode='w', newline='') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        job_url = row['URL']
        driver.get(job_url)
        time.sleep(5)  # Wait for the page to load

        # Get page source and parse it
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Extract job description
        job_details_div = soup.find('div', id='job-details')
        job_description = ' '.join(p.get_text(strip=True) for p in job_details_div.find_all('p')) if job_details_div else 'N/A'

        # Write detailed information to output CSV
        writer.writerow({
            'Title': row['Title'],
            'Company': row['Company'],
            'Location': row['Location'],
            'URL': row['URL'],
            'Job Description': job_description
        })

# Close WebDriver
driver.quit()

print(f"Detailed job information saved to {output_csv_file}")
