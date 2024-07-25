from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time

# Setup Selenium WebDriver for Safari
driver = webdriver.Safari()

# Define the base URL and the search parameters
base_url = "https://www.simplyhired.com"
search_query = "/search?q=software+engineer&l=Philadelphia%2C+PA"
full_url = base_url + search_query

# Normalize job details
def normalize(text):
    return ' '.join(text.split()).strip().lower()

# Scrape a single page
def scrape_page(existing_urls):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_list_ul = soup.find('ul', {'id': 'job-list', 'role': 'list', 'tabindex': '-1'})
    
    # Check if job_list_ul is found
    if job_list_ul is None:
        print("No job list found.")
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

        job_entry = [title, company, location, link]
        
        # Check for duplicates before adding
        if link not in existing_urls:
            job_list.append(job_entry)
            existing_urls.add(link)
    

    print(f"Jobs from the current page:")
    for job in job_list:
        print(job)

    return job_list

# Get the next page URL and navigate to it
def go_to_next_page(previous_url):
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-testid='pageNumberBlockNext']"))
        )
        next_button.click()
        time.sleep(2)  # Allow time for the page to load
        current_url = driver.current_url
        if current_url == previous_url:
            return False
        return current_url
    except Exception as e:
        print("No next page found or failed to click next:", e)
        return False

# Scrape multiple pages
all_jobs = []
seen_urls = set()
driver.get(full_url)
current_url = driver.current_url

while True:
    print(f"Scraping page: {driver.current_url}")
    jobs = scrape_page(seen_urls)
    all_jobs.extend(jobs)
    time.sleep(2)  # Respectful delay between requests
    next_url = go_to_next_page(current_url)
    if not next_url:
        break
    current_url = next_url

# Save results to a CSV file
csv_file = './backend/simplyhired/simplyhired_jobs.csv'
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Title', 'Company', 'Location', 'URL'])
    writer.writerows(all_jobs)

print(f"Scraping completed. {len(all_jobs)} jobs saved to {csv_file}.")

# Close WebDriver
driver.quit()
