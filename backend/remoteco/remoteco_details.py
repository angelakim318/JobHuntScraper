import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.options import Options
from bs4 import BeautifulSoup

# Define the URL and search parameters
base_url = "https://remote.co/remote-jobs/search/?search_keywords=software+engineer"

# Set up Safari options to include user agent
options = Options()
options.add_argument("--headless")
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36")

# Initialize WebDriver
driver = webdriver.Safari(options=options)

# Function to scrape a single page
def scrape_page(url):
    driver.get(url)
    time.sleep(3)  # Allow time for the page to load

    job_cards = driver.find_elements(By.CLASS_NAME, 'SerpJob-jobCard')
    jobs = []

    for job_card in job_cards:
        soup = BeautifulSoup(job_card.get_attribute('outerHTML'), 'html.parser')
        
        try:
            title_element = soup.select_one('h2.chakra-text.css-8rdtm5[data-testid="searchSerpJobTitle"] > a')
            if not title_element:
                continue
            
            job_title = title_element.text.strip()
            job_url = "https://www.simplyhired.com" + title_element['href']
            company = soup.select_one('span[data-testid="companyName"]').text.strip()
            location = soup.select_one('span[data-testid="searchSerpJobLocation"]').text.strip()
            
            jobs.append([job_title, company, location, job_url])
        
        except Exception as e:
            print(f"Error extracting job details: {e}")

    return jobs

# Function to get the pagination links
def get_pagination_links():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    pagination_links = soup.select('nav[aria-label="pagination"] a.chakra-link')
    pages = [link['href'] for link in pagination_links if link['aria-label'] != 'Next page']
    return pages

# Scrape all pages
all_jobs = []
current_page = base_url
while current_page:
    all_jobs.extend(scrape_page(current_page))
    pagination_links = get_pagination_links()
    current_page = pagination_links.pop(0) if pagination_links else None

# Close the WebDriver
driver.quit()

# Save to CSV
with open('./backend/remoteco_jobs_detailed.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Title', 'Company', 'Location', 'URL'])
    writer.writerows(all_jobs)

print(f"Extracted {len(all_jobs)} jobs to remoteco_jobs_detailed.csv")
