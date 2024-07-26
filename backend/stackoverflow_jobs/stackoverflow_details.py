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

        # Extract job details
        job_details_div = soup.find('div', class_='job-company col-lg-9 v2 mb--26')
        title_elem = job_details_div.find('div', class_='title mb-0 fs-16') if job_details_div else None
        company_elem = job_details_div.find('div', class_='name color-01') if job_details_div else None
        location_elem = job_details_div.find('div', class_='location color-01') if job_details_div else None
        job_description_div = soup.find('div', class_='col-lg-9 middlecol')
        
        title = title_elem.get_text(strip=True) if title_elem else 'N/A'
        company = company_elem.get_text(strip=True) if company_elem else 'N/A'
        location = location_elem.get_text(strip=True) if location_elem else 'N/A'
        job_description = ' '.join(p.get_text(strip=True) for p in job_description_div.find_all('p')) if job_description_div else 'N/A'

        # Write detailed information to output CSV
        writer.writerow({
            'Title': title,
            'Company': company,
            'Location': location,
            'URL': row['URL'],
            'Job Description': job_description
        })

# Close WebDriver
driver.quit()

print(f"Detailed job information saved to {output_csv_file}")
