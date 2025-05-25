from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd

def scrape_rozee(keyword):
    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--log-level=3')

    driver = webdriver.Edge(options=options)
    url_keyword = keyword.replace(" ", "%20")
    driver.get(f"https://www.rozee.pk/job/jsearch/q/{url_keyword}")
    time.sleep(5)

    job_data = []
    page = 1

    while True:
        print(f"🔄 Scraping Page {page}...")
        jobs = driver.find_elements(By.CLASS_NAME, "job")

        for job in jobs:
            try:
                title = job.find_element(By.CSS_SELECTOR, ".jhead a").text.strip()

                comp_loc = job.find_element(By.CSS_SELECTOR, ".jhead").text.strip()
                company = comp_loc.split('\n')[0]
                location = comp_loc.split('\n')[1] if len(comp_loc.split('\n')) > 1 else "N/A"

                footer_lines = job.find_element(By.CLASS_NAME, "jfooter").text.strip().split("\n")
                date_posted = footer_lines[0] if len(footer_lines) > 0 else "N/A"
                experience = footer_lines[1] if len(footer_lines) > 1 else "N/A"
                if len(footer_lines) > 2 and ("K" in footer_lines[2] or any(char.isdigit() for char in footer_lines[2])):
                    salary = footer_lines[2]
                else:
                    salary = "N/A"

                job_data.append({
                    "Title": title,
                    "Company": company,
                    "Location": location,
                    "Date_Posted": date_posted,
                    "Experience": experience,
                    "Salary": salary
                })
            except:
                continue

        try:
            next_button = driver.find_element(By.XPATH, "//a[contains(text(),'Next')]")
            if 'disabled' in next_button.get_attribute("class"):
                break  # No more pages
            next_button.click()
            page += 1
            time.sleep(5)
        except:
            print("❌ No more pages or 'Next' button not found.")
            break

    driver.quit()

    df = pd.DataFrame(job_data)
    return df
