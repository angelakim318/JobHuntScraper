import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.safari.options import Options
from bs4 import BeautifulSoup

# Define the URL and search parameters
url = 'https://www.glassdoor.com/Job/philadelphia-pa-us-software-engineer-jobs-SRCH_IL.0,18_IC1152672_KO19,36.htm'

# Set up Safari options to include user agent
options = Options()
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15")

# Initialize WebDriver
driver = webdriver.Safari(options=options)
driver.get(url)
time.sleep(5)  # Wait for the page to load

# Scroll to load all job listings
for i in range(10):
    ActionChains(driver).send_keys(Keys.END).perform()
    time.sleep(2 + i)  # Increase delay to mimic human behavior

# Parse the page source with BeautifulSoup
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# Define columns for the CSV
fieldnames = ['Title', 'Company', 'Location', 'Posted Date', 'URL']

# Open the output CSV file
with open('./backend/glassdoor/glassdoor_jobs.csv', mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    # Find all job listings
    job_cards = soup.find_all('li', class_='jobListItem')  # Corrected class name

    for job in job_cards:
        try:
            title = job.find('a', class_='jobTitle').text.strip()  # Corrected class name
            company = job.find('span', class_='compactEmployerName').text.strip()  # Corrected class name
            location = job.find('div', class_='jobCard_location').text.strip()  # Corrected class name
            posted_date = job.find('div', class_='jobCard_listingAge').text.strip()  # Corrected class name
            url = job.find('a', class_='jobTitle')['href']  # Corrected class name
        except AttributeError:
            continue

        # Write to CSV
        writer.writerow({
            'Title': title,
            'Company': company,
            'Location': location,
            'Posted Date': posted_date,
            'URL': 'https://www.glassdoor.com' + url  # Ensure the URL is complete
        })

# Close the WebDriver
driver.quit()

print("Data saved to ./backend/glassdoor/glassdoor_jobs.csv")
