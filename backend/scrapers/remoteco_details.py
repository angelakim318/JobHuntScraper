from selenium import webdriver
from selenium.webdriver.safari.service import Service
from selenium.webdriver.safari.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import os

def scrape_remoteco_job_details():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(script_dir, '..', 'data', 'remoteco_jobs.csv')
    output_csv = os.path.join(script_dir, '..', 'data', 'remoteco_jobs_detailed.csv')
    
    print(f"Running remoteco script in {os.getcwd()}")
    
    # Define Safari options
    safari_options = Options()

    # Initialize WebDriver with Safari options
    driver = webdriver.Safari(service=Service(), options=safari_options)

    # Create a list to store detailed job information
    detailed_jobs = []

    # Open CSV file and read the job URLs
    with open(input_csv, mode='r') as file:
        reader = csv.DictReader(file)
        jobs = list(reader)

    # Iterate through each job and scrape detailed information
    for job in jobs:
        title = job['Title']
        company = job['Company']
        job_type = job['Job Type']
        url = job['URL']

        # Open job details page
        driver.get(url)
        time.sleep(5)  # Wait for page to load

        # Get page source and parse with BeautifulSoup
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Extract detailed job information
        location_element = soup.find('div', class_='location_sm')
        location = location_element.text.strip() if location_element else 'N/A'

        benefits_element = soup.find('div', class_='benefits_sm row')
        benefits = benefits_element.text.strip() if benefits_element else 'N/A'

        posted_date_element = soup.find('time')
        posted_date = posted_date_element['datetime'] if posted_date_element else 'N/A'

        # Append detailed job information to the list
        detailed_jobs.append({
            'Title': title,
            'Company': company,
            'Job Type': job_type,
            'URL': url,
            'Location': location,
            'Benefits': benefits,
            'Posted Date': posted_date
        })

        print(f"Scraped details for job: {title}")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    # Save detailed job information to a new CSV file
    fieldnames = ['Title', 'Company', 'Job Type', 'URL', 'Location', 'Benefits', 'Posted Date']
    with open(output_csv, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for job in detailed_jobs:
            writer.writerow(job)

    print(f"Detailed job data saved to {output_csv}")

    # Close WebDriver
    driver.quit()

# If script is run directly, call the function
if __name__ == '__main__':
    scrape_remoteco_job_details()