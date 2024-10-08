import sys
import os

# Path to the backend folder added to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time
import logging
from backend.models.models import Job, DATABASE_URL  # Import after setting up sys.path

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def scrape_simplyhired_jobs():
    # Check if data already exists in the database
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    if session.query(Job).filter(Job.url.like('%simplyhired.com%')).first():
        logger.debug("Data for SimplyHired already exists in the database. Skipping scraping.")
        return
    session.close()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_csv = os.path.join(script_dir, '..', 'data', 'simplyhired_jobs.csv')

    logger.debug(f"Running simplyhired script in {os.getcwd()}")

    try:
        # Setup Selenium WebDriver for Safari
        driver = webdriver.Safari()

        # Define the base URL and the search parameters
        base_url = "https://www.simplyhired.com"
        search_query = "/search?q=software+engineer&l=Philadelphia%2C+PA"
        full_url = base_url + search_query

        # Normalize job details
        def normalize(text):
            return ' '.join(text.split()).strip()

        # Scrape a single page
        def scrape_page(existing_urls):
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            job_list_ul = soup.find('ul', {'id': 'job-list', 'role': 'list', 'tabindex': '-1'})

            # Check if job_list_ul is found
            if job_list_ul is None:
                logger.debug("No job list found.")
                return []

            job_cards = job_list_ul.find_all('li', class_='css-0')

            job_list = []
            for job in job_cards:
                title_elem = job.find('h2', class_='chakra-text css-8rdtm5').find('a')
                if title_elem:
                    title = normalize(title_elem.text)
                    link = base_url + title_elem['href']
                else:
                    title = 'N/A'
                    link = 'N/A'

                company_elem = job.find('span', {'data-testid': 'companyName'})
                company = normalize(company_elem.text) if company_elem else 'N/A'

                location_elem = job.find('span', {'data-testid': 'searchSerpJobLocation'})
                location = normalize(location_elem.text) if location_elem else 'N/A'

                job_entry = [title, company, location, link, 'N/A']  

                # Check for duplicates before adding
                if link not in existing_urls:
                    job_list.append(job_entry)
                    existing_urls.add(link)

            logger.debug(f"Jobs from the current page:")
            for job in job_list:
                logger.debug(job)

            return job_list

        # Get the next page URL and navigate to it
        def go_to_next_page():
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-testid='pageNumberBlockNext']"))
                )
                next_button.click()
                time.sleep(3)  # Allow time for the page to load
                return True
            except Exception as e:
                logger.debug("No next page found or failed to click next:", e)
                return False

        # Scrape multiple pages
        all_jobs = []
        seen_urls = set()
        visited_urls = set()
        driver.get(full_url)

        while True:
            current_url = driver.current_url
            if current_url in visited_urls:
                logger.debug("Reached a previously visited URL, stopping the scraper.")
                break
            visited_urls.add(current_url)

            logger.debug(f"Scraping page: {current_url}")
            jobs = scrape_page(seen_urls)
            all_jobs.extend(jobs)
            time.sleep(2)  # Delay between requests
            if not go_to_next_page():
                break

        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)

        # Save results to a CSV file
        with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Title', 'Company', 'Location', 'URL', 'Job Type'])  
            writer.writerows(all_jobs)

        logger.debug(f"Scraping completed. {len(all_jobs)} jobs saved to {output_csv}.")

    except Exception as e:
        logger.error(f"Error occurred: {e}")

    finally:
        # Close WebDriver
        driver.quit()

# If script is run directly, call the function
if __name__ == '__main__':
    scrape_simplyhired_jobs()
