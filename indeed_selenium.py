import time
import csv
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from fake_useragent import UserAgent

class RozeeScraper:
    def __init__(self):
        self.job_data = []
        self.ua = UserAgent()
        self.driver = None
        self._setup_driver()
        
    def _setup_driver(self):
        """Configure Chrome with Rozee.pk specific settings"""
        options = Options()
        
        # Stealth settings
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"user-agent={self.ua.random}")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.service = Service(executable_path="D:\\Foodpanda project\\chromedriver.exe")
            self.driver = webdriver.Chrome(service=self.service, options=options)
            self.wait = WebDriverWait(self.driver, 20)
            
            # Mask selenium detection
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
        except Exception as e:
            print(f"Failed to initialize WebDriver: {e}")
            raise

    def _random_delay(self):
        """Random delay to mimic human behavior"""
        time.sleep(random.uniform(2.0, 5.0))

    def scrape_jobs(self, search_term="software", max_pages=3):
        """Main scraping function for Rozee.pk"""
        try:
            base_url = f"https://www.rozee.pk/search/jobs/{search_term}"
            
            for page in range(1, max_pages + 1):
                url = f"{base_url}/{page}" if page > 1 else base_url
                print(f"Scraping page {page}: {url}")
                
                if not self._load_page(url):
                    print("Possible blocking detected, trying bypass...")
                    self._bypass_blocking()
                    continue
                
                self._human_like_interaction()
                self._scroll_page()
                
                if not self._extract_jobs():
                    print("No job cards found")
                    break
                
                self._random_delay()
                
        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            if self.driver:
                self.driver.quit()
            
        return self.job_data
    
    def _load_page(self, url):
        """Load Rozee.pk page with error handling"""
        try:
            self.driver.get(url)
            self._random_delay()
            
            # Check for blocking
            if "blocked" in self.driver.page_source.lower():
                return False
                
            # Wait for job cards
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.job-listing, .no-results'))
                )
                return True
            except TimeoutException:
                return False
                
        except Exception as e:
            print(f"Page load error: {e}")
            return False

    def _bypass_blocking(self):
        """Attempt to bypass blocking"""
        try:
            print("Changing user agent and clearing cookies...")
            self.driver.delete_all_cookies()
            new_ua = self.ua.random
            self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": new_ua})
            time.sleep(3)
            return True
        except Exception as e:
            print(f"Bypass failed: {e}")
            return False

    def _human_like_interaction(self):
        """Mimic human behavior"""
        try:
            actions = ActionChains(self.driver)
            for _ in range(random.randint(2, 4)):
                x = random.randint(-100, 100)
                y = random.randint(-100, 100)
                actions.move_by_offset(x, y).perform()
                time.sleep(random.uniform(0.5, 1.5))
        except Exception as e:
            print(f"Interaction error: {e}")

    def _scroll_page(self):
        """Scroll page to load all content"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                self.driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(random.uniform(1.0, 2.0))
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        except Exception as e:
            print(f"Scrolling error: {e}")

    def _extract_jobs(self):
        """Extract job listings from current page"""
        try:
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, '.job-listing')
            
            if not job_cards:
                return False
                
            print(f"Found {len(job_cards)} jobs on page")
            
            for card in job_cards:
                try:
                    title = self._get_element_text(card, '.job-title a', "No Title")
                    company = self._get_element_text(card, '.company-name', "No Company")
                    location = self._get_element_text(card, '.job-location', "No Location")
                    salary = self._get_element_text(card, '.salary', "Not Specified")
                    
                    self.job_data.append({
                        'Title': title,
                        'Company': company,
                        'Location': location,
                        'Salary': salary,
                        'Timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                except Exception as e:
                    print(f"Error processing job card: {e}")
                    continue
                    
            return True
            
        except Exception as e:
            print(f"Extraction error: {e}")
            return False

    def _get_element_text(self, parent, selector, default):
        """Helper to safely get element text"""
        try:
            return parent.find_element(By.CSS_SELECTOR, selector).text.strip()
        except NoSuchElementException:
            return default

    def save_to_csv(self, filename="rozee_jobs.csv"):
        """Save results to CSV"""
        if not self.job_data:
            print("No data to save")
            return False
        
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=self.job_data[0].keys())
                writer.writeheader()
                writer.writerows(self.job_data)
            print(f"Successfully saved {len(self.job_data)} jobs to {filename}")
            return True
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return False

if __name__ == "__main__":
    print("Starting Rozee.pk Scraper...")
    
    try:
        scraper = RozeeScraper()
        jobs = scraper.scrape_jobs(search_term="software", max_pages=3)
        
        if jobs:
            scraper.save_to_csv()
            print(f"\nSuccess! Collected {len(jobs)} jobs from Rozee.pk")
        else:
            print("\nNo jobs collected. Try:")
            print("- Different search terms")
            print("- Running during off-peak hours")
            print("- Using a VPN")
            
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        print("Scraping completed")