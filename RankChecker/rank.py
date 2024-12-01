import requests
import random
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import time
from halo import Halo
from termcolor import colored
from typing import List, Optional

# Set up the spinner animation
spinner = Halo(text='', spinner='dots')
spinner.start()

# Inputs
keyword = 'running shoes'
sitename = "https://www.adidas.com/"
competitors = [
    "https://www.nike.com",
    "https://www.reebok.com",
    "https://www.ascics.com",
    "https://www.hoka.com"
]

# User agent strings
mobile_agents = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/114.0.5735.99 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/114.1 Mobile/15E148 Safari/605.1.15',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 EdgiOS/114.0.5735.99',
]

desktop_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15; rv:105.0) Gecko/20100101 Firefox/105.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15; rv:15.0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
]

def clean_url(url: str) -> Optional[str]:
    """Cleans a given URL by extracting the portion starting from 'https://'. Returns None if not found."""
    start = url.find('https://')
    if start == -1:
        return None

    end = url.find('&ved', start)
    return url[start:end] if end != -1 else url[start:]

def rank_check(sitename: str, serp_df: pd.DataFrame, keyword: str, entry_type: str) -> pd.DataFrame:
    """Checks the rank of the sitename in the SERP DataFrame."""
    ranks = [(keyword, idx + 1, url, datetime.date.today().strftime("%d-%m-%Y"), entry_type)
             for idx, url in enumerate(serp_df['URLs']) if sitename in str(url)]
    
    return pd.DataFrame(ranks, columns=['Keyword', 'Rank', 'URLs', 'Date', 'Type']) if ranks else pd.DataFrame(columns=['Keyword', 'Rank', 'URLs', 'Date', 'Type'])

def get_data(keyword: str, sitename: str, device: str) -> pd.DataFrame:
    """Fetches search results from Google and returns a DataFrame with URLs."""
    google_url = f'https://www.google.com/search?num=100&q={keyword}'
    
    useragent = random.choice(mobile_agents if device.lower() == 'mobile' else desktop_agents)
    headers = {'User-Agent': useragent}
    
    print(colored(f"- Checking {'Mobile' if device.lower() == 'mobile' else 'Desktop'} Rankings", 'black', attrs=['bold']))
    
    response = requests.get(google_url, headers=headers)
    
    if response.status_code != 200:
        error_message = f'Failed to retrieve data, status code: {response.status_code}'
        print(colored(error_message, 'red'))
        return pd.DataFrame({'status': [error_message]})
    
    soup = BeautifulSoup(response.text, 'html.parser')
    urls = soup.find_all('div', class_="P8ujBc" if device.lower() == 'mobile' else "yuRUbf")
    
    data = [clean_url(div.find('a')['href']) for div in urls if div.find('a')]
    
    serp_df = pd.DataFrame(data, columns=['URLs']).dropna(subset=['URLs'])
    
    results = rank_check(sitename, serp_df, keyword, "My Site")
    
    print(colored(f"- Rankings results for {sitename}", 'black', attrs=['bold']))
    print(results)

    for competitor in competitors:
        competitor_results = rank_check(competitor, serp_df, keyword, "Competitor")
        results = pd.concat([results, competitor_results], ignore_index=True)

    return results.sort_values(by='Rank')

# Execute ranking checks
mobile_results = get_data(keyword, sitename, 'mobile')
time.sleep(5)
desktop_results = get_data(keyword, sitename, 'desktop')

# Save results to Excel
try:
    with pd.ExcelWriter(f"{keyword}.xlsx", engine='openpyxl') as writer:
        mobile_results.to_excel(writer, sheet_name='Mobile', index=False)
        desktop_results.to_excel(writer, sheet_name='Desktop', index=False)
except Exception as e:
    print('Error saving data:', e)

# Stop the spinner
spinner.stop_and_persist(symbol='🤖'.encode('utf-8'), text='All Checks have been finalized!')
