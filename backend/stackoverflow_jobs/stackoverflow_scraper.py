import csv
from selenium import webdriver
from selenium.webdriver.safari.service import Service
from selenium.webdriver.safari.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Define URL for job search
url = 'https://stackoverflow.jobs/search/jobs?searchTerm=software%20engineer&location=Philadelphia,%20USA'

# Define Safari options
safari_options = Options()

# Initialize WebDriver with Safari options
driver = webdriver.Safari(service=Service(), options=safari_options)
driver.get(url)

# Wait for the job listings to load
time.sleep(5)  

# Create CSV file to store job listings
csv_file = './backend/stackoverflow_jobs/stackoverflow_jobs.csv'
fieldnames = ['Title', 'Company', 'Location', 'Posted Date', 'URL']
with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    while True:
        # Get the job listings on the current page
        job_cards = driver.find_elements(By.CSS_SELECTOR, 'a.job-list-item')

        if not job_cards:
            print("No job cards found on the page.")
            #print(driver.page_source)  # Print the HTML source of the page for debugging

        for job_card in job_cards:
            try:
                title = job_card.find_element(By.CSS_SELECTOR, 'div.job-name').text
                company = job_card.find_element(By.CSS_SELECTOR, 'div.c-name').text
                location = job_card.find_element(By.CSS_SELECTOR, 'div.location').text
                posted_date = job_card.find_element(By.CSS_SELECTOR, 'div.posted').text
                job_url = job_card.get_attribute('href')

                writer.writerow({
                    'Title': title,
                    'Company': company,
                    'Location': location,
                    'Posted Date': posted_date,
                    'URL': job_url
                })
                print(f"Job found: {title}, {company}, {location}, {posted_date}, {job_url}")
            except Exception as e:
                print(f"Error extracting data for a job card: {e}")

        try:
            # Click "Next" button to go to the next page of results
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.page-link[aria-label="Go to next page"]'))
            )
            next_button.click()
            time.sleep(5)  
        except Exception as e:
            print(f"No more 'Next' button found or error occurred: {e}")
            break

driver.quit()
print(f"Data saved to {csv_file}")
