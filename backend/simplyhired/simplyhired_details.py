import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.options import Options
from bs4 import BeautifulSoup

# Set up Safari options
options = Options()
options.add_argument("--headless")
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36")

# Initialize WebDriver
driver = webdriver.Safari(options=options)

# Function to scrape job details from a given URL
def scrape_job_details(url):
    driver.get(url)
    time.sleep(3)  # Allow time for the page to load
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract job details
    job_details = {}
    
    title_elem = soup.find('h1', {'data-testid': 'viewJobTitle'})
    job_details['Title'] = title_elem.text.strip() if title_elem else 'N/A'
    
    company_elem = soup.find('span', {'data-testid': 'detailText'})
    job_details['Company'] = company_elem.text.strip() if company_elem else 'N/A'
    
    location_elem = soup.find_all('span', {'data-testid': 'detailText'})
    job_details['Location'] = location_elem[1].text.strip() if len(location_elem) > 1 else 'N/A'
    
    # Find posted date element
    posted_date_elem = soup.find('span', {'data-testid': 'viewJobBodyJobPostingTimestamp'})
    if posted_date_elem:
        date_text_elem = posted_date_elem.find('span', {'data-testid': 'detailText'})
        job_details['Posted Date'] = date_text_elem.text.strip() if date_text_elem else 'N/A'
    else:
        job_details['Posted Date'] = 'N/A'
    
    qualifications_list = soup.find_all('span', {'data-testid': 'viewJobQualificationItem'})
    job_details['Qualifications'] = [qual.text.strip() for qual in qualifications_list]
    
    job_desc_elem = soup.find('div', {'data-testid': 'viewJobBodyJobFullDescriptionContent'})
    job_details['Job Description'] = job_desc_elem.get_text(separator=' ').strip() if job_desc_elem else 'N/A'
    
    job_details['URL'] = url

    return job_details

# Read URLs from simplyhired_jobs.csv
input_csv = './backend/simplyhired/simplyhired_jobs.csv'
output_csv = './backend/simplyhired/simplyhired_jobs_detailed.csv'

# Initialize the list to hold job details
all_job_details = []

# Read job URLs from the CSV file and scrape details
with open(input_csv, newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        job_url = row['URL']
        print(f"Scraping details from: {job_url}")
        job_details = scrape_job_details(job_url)
        all_job_details.append(job_details)
        time.sleep(2)  # Respectful delay between requests

# Save detailed job information to a new CSV file
with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
    fieldnames = ['Title', 'Company', 'Location', 'Posted Date', 'Qualifications', 'Job Description', 'URL']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_job_details)

print(f"Scraping completed. Job details saved to {output_csv}.")

# Close WebDriver
driver.quit()
