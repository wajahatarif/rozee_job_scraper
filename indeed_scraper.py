import requests
from bs4 import BeautifulSoup

url = "https://www.indeed.com/jobs?q=software+developer&l="

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "DNT": "1",  # Do Not Track Request Header
    "Connection": "keep-alive"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = soup.find_all("h2", class_="jobTitle", limit=5)

    if not jobs:
        print("No jobs found. Website structure might have changed.")
    else:
        print("Top 5 job titles:")
        for job in jobs:
            title = job.get_text(strip=True)
            print(title)
else:
    print(f"Failed to retrieve page, status code: {response.status_code}")
