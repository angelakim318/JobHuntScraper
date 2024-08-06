import sys
import os

# Path to the backend folder added to system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from selenium import webdriver
from selenium.webdriver.safari.service import Service
from selenium.webdriver.safari.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import logging
from backend.models.models import Job, DATABASE_URL  # Import after setting up sys.path

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def scrape_remoteco_jobs():
    # Check if data already exists in database
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    if session.query(Job).filter(Job.url.like('%remote.co%')).first():
        logger.debug("Data for Remote.co already exists in the database. Skipping scraping.")
        return
    session.close()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_csv = os.path.join(script_dir, '..', 'data', 'remoteco_jobs.csv')
    
    logger.debug(f"Running remoteco script in {os.getcwd()}")

    try:
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
                logger.debug("Looking for 'Load more listings' button...")
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.load_more_jobs"))
                )
                logger.debug("Button found, clicking...")
                driver.execute_script("arguments[0].click();", load_more_button)
                time.sleep(5)  # Wait for jobs to load
            except TimeoutException:
                logger.debug("No more 'Load more listings' button found or timed out.")
                break
            except Exception as e:
                logger.debug("An error occurred while looking for the 'Load more listings' button: %s", e)
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

        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)

        # Save data to a CSV file
        fieldnames = ['Title', 'Company', 'Job Type', 'URL']
        with open(output_csv, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for job in jobs:
                writer.writerow({
                    'Title': job['title'],
                    'Company': job['company'],
                    'Job Type': job['job_type'],
                    'URL': f"https://remote.co{job['url']}"
                })

        logger.debug(f"Data saved to {output_csv}")

    except Exception as e:
        logger.error(f"Error occurred: {e}")

    finally:
        # Close WebDriver
        driver.quit()

# If script is run directly, call the function
if __name__ == '__main__':
    scrape_remoteco_jobs()
