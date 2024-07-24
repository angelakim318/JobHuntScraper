import csv
from selenium import webdriver
from selenium.webdriver.safari.service import Service
from selenium.webdriver.safari.options import Options
import time
from bs4 import BeautifulSoup

# Read the existing CSV file
input_csv_file = 'remoteco_jobs.csv'
output_csv_file = 'remoteco_jobs_detailed.csv'

# Define Safari options
safari_options = Options()
# Initialize WebDriver with Safari options
driver = webdriver.Safari(service=Service(), options=safari_options)

# Define columns for the detailed CSV
fieldnames = ['Title', 'Company', 'Job Type', 'URL', 'Location', 'Benefits', 'Posted Date']

# Open the input CSV file and create the output CSV file
with open(input_csv_file, mode='r', newline='') as infile, open(output_csv_file, mode='w', newline='') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        job_url = row['URL']
        driver.get(job_url)
        time.sleep(5)  # Wait for the page to load

        # Get the page source and parse it
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Extract detailed information using correct class names
        location = soup.find('div', class_='col-10 col-sm-11 pl-1').text.strip() if soup.find('div', class_='col-10 col-sm-11 pl-1') else 'N/A'
        benefits = soup.find('div', class_='benefits_sm row').text.strip() if soup.find('div', class_='benefits_sm row') else 'N/A'
        
        # Correctly extract the posted date using the datetime attribute
        date_element = soup.find('time', datetime=True)
        posted_date = date_element['datetime'] if date_element and 'datetime' in date_element.attrs else 'N/A'

        # Write the detailed information to the output CSV
        writer.writerow({
            'Title': row['Title'],
            'Company': row['Company'],
            'Job Type': row['Job Type'],
            'URL': row['URL'],
            'Location': location,
            'Benefits': benefits,
            'Posted Date': posted_date
        })

# Close the WebDriver
driver.quit()

print(f"Detailed job information saved to {output_csv_file}")
