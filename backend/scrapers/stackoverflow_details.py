import csv
from selenium import webdriver
from selenium.webdriver.safari.service import Service
from selenium.webdriver.safari.options import Options
import time
from bs4 import BeautifulSoup
import os

def scrape_stackoverflow_job_details():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(script_dir, '..', 'data', 'stackoverflow_jobs.csv')
    output_csv = os.path.join(script_dir, '..', 'data', 'stackoverflow_jobs_detailed.csv')

    print(f"Running stackoverflow script in {os.getcwd()}")

    # Define Safari options
    safari_options = Options()

    # Initialize WebDriver with Safari options
    driver = webdriver.Safari(service=Service(), options=safari_options)

    # Define columns for CSV
    fieldnames = ['Title', 'Company', 'Location', 'URL', 'Job Description']

    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    # Open input CSV file and create output CSV file
    with open(input_csv, mode='r', newline='') as infile, open(output_csv, mode='w', newline='') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            job_url = row['URL']
            driver.get(job_url)
            time.sleep(5)  # Wait for page to load

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

    print(f"Detailed job information saved to {output_csv}")

# If script is run directly, call the function
if __name__ == '__main__':
    scrape_stackoverflow_job_details()