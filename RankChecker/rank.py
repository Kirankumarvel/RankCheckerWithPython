import requests
from bs4 import BeautifulSoup
import openpyxl
from datetime import datetime
import time

# Inputs
keyword = 'running shoes'
sitename = "https://www.adidas.com/"
competitors = [
    "https://www.nike.com",
    "https://www.reebok.com",
    "https://www.asics.com",
    "https://www.hoka.com"
]

# Function to scrape rankings
def get_rankings(url):
    # Set headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    try:
        # Make the request with headers (and proxies if uncommented)
        response = requests.get(url, headers=headers)  # Uncomment proxies if needed
        response.raise_for_status()  # Raise an error for bad responses
        
        soup = BeautifulSoup(response.content, 'html.parser')

        # Example logic to find rank (customize based on actual HTML structure)
        rank_element = soup.find('div', class_='desired-class')  # Update this selector based on actual site structure
        
        if rank_element:
            rank = int(rank_element.text.strip())  # Extract rank as integer
        else:
            rank = None
        
        return {
            'url': url,
            'rank': rank,
            'date': datetime.now().strftime("%m-%d-%Y"),
            'type': 'My Site' if url == sitename else 'Competitor'
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Collect rankings
rankings = []
urls = [sitename] + competitors

for url in urls:
    result = get_rankings(url)
    if result:
        rankings.append(result)
    time.sleep(5)  # Wait for 5 seconds before the next request to avoid being blocked

# Save results to Excel
wb = openpyxl.Workbook()
ws_mobile = wb.active
ws_mobile.title = "Rankings"

# Write header
ws_mobile.append(["Keyword", "Rank", "URL", "Date", "Type"])

# Write data
for ranking in rankings:
    ws_mobile.append([keyword, ranking['rank'], ranking['url'], ranking['date'], ranking['type']])

# Save the workbook
file_name = f"{keyword.replace(' ', '_')}.xlsx"
wb.save(file_name)
print(f"Results saved to {file_name}")
