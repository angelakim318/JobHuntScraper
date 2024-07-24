from selenium import webdriver
from selenium.webdriver.safari.service import Service
from selenium.webdriver.safari.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv

# Define Safari options
safari_options = Options()

# Initialize WebDriver with Safari options
driver = webdriver.Safari(service=Service(), options=safari_options)

# Define URL for job search
url = 'https://remote.co/remote-jobs/search/?search_keywords=software+engineer'

# Open URL
driver.get(url)

# Wait for page to fully load
time.sleep(5)  

# Click 'Load more listings' until all jobs are loaded
while True:
    try:
        print("Looking for 'Load more listings' button...")
        load_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.load_more_jobs"))
        )
        print("Button found, clicking...")
        driver.execute_script("arguments[0].click();", load_more_button)
        time.sleep(5)  # Wait for jobs to load
    except Exception as e:
        print("No more 'Load more listings' button found or error occurred:", e)
        break

# Get page source after all jobs are loaded
html = driver.page_source

# Parse HTML content using BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Find all job postings on page
job_elements = soup.find_all('div', class_='job_listing')

# Extract job information
jobs = []
for job_element in job_elements:
    title_element = job_element.find('a', class_='font-weight-bold larger stretched-link')
    title = title_element.text if title_element else 'N/A'
    url = title_element['href'] if title_element else 'N/A'
    
    company_and_type_element = job_element.find('p', class_='m-0 text-secondary')
    company_and_type_text = company_and_type_element.text.strip() if company_and_type_element else 'N/A'
    
    # Split company and job type based on the | character
    parts = company_and_type_text.split('|')
    company = parts[0].strip() if len(parts) > 0 else 'N/A'
    job_type = parts[1].strip() if len(parts) > 1 else 'N/A'
    
    jobs.append({
        'title': title,
        'company': company,
        'job_type': job_type,
        'url': url
    })

# Save data to a CSV file
csv_file = './backend/remoteco/remoteco_jobs.csv'
fieldnames = ['Title', 'Company', 'Job Type', 'URL']
with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for job in jobs:
        writer.writerow({
            'Title': job['title'],
            'Company': job['company'],
            'Job Type': job['job_type'],
            'URL': f"https://remote.co{job['url']}"
        })

print(f"Data saved to {csv_file}")

# Close WebDriver
driver.quit()
