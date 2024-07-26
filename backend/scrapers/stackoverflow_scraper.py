from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time

# Setup Selenium WebDriver for Safari
driver = webdriver.Safari()

# Define the URL with search parameters
url = "https://stackoverflow.jobs/search/jobs?searchTerm=software%20engineer&location=Philadelphia,%20USA"

# Normalize job details
def normalize(text):
    return ' '.join(text.split()).strip()

# Scrape job details from the listing
def scrape_job_listing(soup):
    job_details_list = []

    # Find the div that contains the job cards
    job_cards_container = soup.find('div', class_='job-cards')
    if not job_cards_container:
        print("No job cards container found.")
        return job_details_list

    # Find all job cards within the container
    job_cards = job_cards_container.find_all('a', class_='job-list-item')
    if not job_cards:
        print("No job cards found.")
        return job_details_list

    for job in job_cards:
        title_elem = job.find('div', class_='job-name')
        company_elem = job.find('div', class_='c-name')
        location_elem = job.find('div', class_='location')
        link_elem = job.get('href')

        if title_elem:
            title = normalize(title_elem.text)
        else:
            title = 'N/A'

        company = normalize(company_elem.text) if company_elem else 'N/A'
        location = normalize(location_elem.text) if location_elem else 'N/A'
        link = link_elem if link_elem else 'N/A'

        job_details_list.append({
            'title': title,
            'company': company,
            'location': location,
            'link': link,
        })

    return job_details_list

# Scrape a single page
def scrape_page(existing_urls):
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    job_details_list = scrape_job_listing(soup)

    job_list = []

    for job in job_details_list:
        job_entry = [job['title'], job['company'], job['location'], job['link']]

        # Check for duplicates before adding
        if job['link'] not in existing_urls:
            job_list.append(job_entry)
            existing_urls.add(job['link'])
        else:
            print(f"Duplicate job found: {job['title']}")

    print(f"Jobs from the current page:")
    for job in job_list:
        print(job)

    return job_list

# Get the next page URL and navigate to it
def go_to_next_page(previous_url):
    try:
        # Retry logic for handling stale element exceptions
        attempts = 3
        while attempts > 0:
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[aria-label='Go to next page']"))
                )
                next_button.click()
                time.sleep(3)  # Wait for page to load
                new_url = driver.current_url
                if new_url != previous_url:
                    return new_url
                return False
            except Exception as e:
                print(f"Retrying next page click due to: {e}")
                attempts -= 1
                if attempts == 0:
                    raise
    except Exception as e:
        print("No next page found or failed to click next:", e)
        return False

# Scrape multiple pages
all_jobs = []
seen_urls = set()
driver.get(url)
current_url = driver.current_url

while True:
    print(f"Scraping page: {driver.current_url}")
    
    # Wait for job cards to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "job-list-item"))
    )
    
    jobs = scrape_page(seen_urls)
    all_jobs.extend(jobs)
    time.sleep(2)  # Delay between requests
    next_url = go_to_next_page(current_url)
    if not next_url or next_url == current_url:
        break
    current_url = next_url

# Save results to a CSV file
csv_file = './backend/data/stackoverflow_jobs.csv'
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Title', 'Company', 'Location', 'URL'])
    writer.writerows(all_jobs)

print(f"Scraping completed. {len(all_jobs)} jobs saved to {csv_file}.")

# Close WebDriver
driver.quit()