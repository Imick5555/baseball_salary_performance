import pandas as pd
import asyncio
import json
import time
import aiohttp
import cloudscraper
from bs4 import BeautifulSoup, Comment
from typing import Optional

CF_CLEARANCE_VALUE = "PJDkOHnomh5mSmsLCmxBOr_s3.n6l32oCj30gs5xtQg-1764910639-1.2.1.1-noJsYKc4Unwuax6UZ9pFUDXjjjiPMQ6cOENb2nBVWd_mUAQ64h0Gd1OXYb0fFmJEUuCzoHGV_XInPyA.8QrgW_kkjDPTkeg4TSSt.3O32vEc6HyGtGy4lomj4wAc6T0kNaKxCxmGr_rHrRK7N8B1mcVZLDFl.x7tzi8BqhC7dEDAZ24C9vIzMbROo.Ue6g2TCJNVf.eI3TiYpQ_meOyY7bdctSHoBCG3_9y9JmZX3r8"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}



def create_http_headers() -> dict[str, str]:
    """Create headers that mimic a real browser to avoid being blocked"""
    return {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }


def parse_salary_table_from_soup(soup: BeautifulSoup) -> dict[int, int]:
    """Extract salary data from the baseball-reference salary table using BeautifulSoup"""
    salary_dict = {}
   
    # First try to find the table normally
    salary_table = soup.find('table', {'id': 'br-salaries'})
   
    # If not found, look for it in HTML comments (common pattern for baseball-reference)
    if not salary_table:
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            if 'id="br-salaries"' in comment:
                comment_soup = BeautifulSoup(comment, 'html.parser')
                salary_table = comment_soup.find('table', {'id': 'br-salaries'})
                if salary_table:
                    break
   
    if not salary_table:
        return salary_dict
   
    rows = salary_table.find_all('tr')
    if not rows:
        return salary_dict
   
    header_row = rows[0]
    headers = [th.get_text().strip() for th in header_row.find_all(['th', 'td'])]
   
    try:
        year_col_idx = headers.index('Year')
        salary_col_idx = headers.index('Salary')
    except ValueError:
        return salary_dict
   
    for row in rows[1:]:
        cells = row.find_all(['td', 'th'])
        if len(cells) <= max(year_col_idx, salary_col_idx):
            continue
           
        year_text = cells[year_col_idx].get_text().strip()
        salary_text = cells[salary_col_idx].get_text().strip()
       
        if year_text.isdigit() and len(year_text) == 4:
            try:
                year = int(year_text)
                if 2018 <= year <= 2025:
                    if salary_text and salary_text.startswith('$'):
                        salary_clean = salary_text.replace("$", "").replace(",", "").strip()
                        if salary_clean:
                            try:
                                salary = int(salary_clean)
                                salary_dict[year] = salary
                            except ValueError:
                                pass
            except ValueError:
                continue
   
    return salary_dict

async def scrape_salary_from_url(url: str, session: aiohttp.ClientSession) -> dict[int, int]:
    """Scrape salary data from a baseball-reference player page using HTTP GET"""
    print(f"Starting to scrape {url}.")
   
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status != 200:
                print(f"Failed to fetch {url}: HTTP {response.status}")
                return {}
           
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            salary_dict = parse_salary_table_from_soup(soup)
           
            print(f"Done scraping {url}. Found {len(salary_dict)} salary entries.")
            return salary_dict
           
    except asyncio.TimeoutError:
        print(f"Timeout while scraping {url}")
        return {}
    except aiohttp.ClientError as e:
        print(f"HTTP error while scraping {url}: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error while scraping {url}: {e}")
        return {}


def extract_unique_links(csv_path: str, output_json_path: str) -> None:
    """Extract unique player links from CSV and save as JSON"""
    df = pd.read_csv(csv_path)
   
    url_to_player = df.dropna(subset=['Player_Link']).drop_duplicates(subset=['Player_Link']).set_index('Player_Link')['Player'].to_dict()
    unique_urls = df['Player_Link'].dropna().unique().tolist()
    links_with_ids = [{"id": i + 1, "url": url, "player": url_to_player[url]} for i, url in enumerate(unique_urls)]
   
    with open(output_json_path, 'w') as f:
        json.dump(links_with_ids, f, indent=2)
   
    print(f"Extracted {len(links_with_ids)} unique links and saved to {output_json_path}")

def scrape_with_cloudscraper(url: str, scraper) -> dict[int, int]:
    print(f"Scraping {url}")
    try:
        html = scraper.get(url, timeout=30).text
        soup = BeautifulSoup(html, 'html.parser')
        return parse_salary_table_from_soup(soup)
    except Exception as e:
        print(f"Failed {url}: {e}")
        return {}
    
def churn_with_cloudscraper():
    # This bypasses Cloudflare ~80–90% of the time
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False},
        delay=10
    )

    with open("unique_links.json", "r") as f:
        links = json.load(f)

    # Resume logic same as yours
    try:
        with open("salaries_again.json", "r") as f:
            existing = json.load(f)
    except:
        existing = []

    existing_ids = {x['id'] for x in existing}
    remaining = [l for l in links if l['id'] not in existing_ids]

    results = {e['id']: e for e in existing}

    for link in remaining:
        salary_data = scrape_with_cloudscraper(link['url'], scraper)
        results[link['id']] = {
            "id": link['id'],
            "player": link['player'],
            "salaries": salary_data
        }

        # Save on every player
        with open("salaries.json", "w") as f:
            json.dump(sorted(results.values(), key=lambda x: x['id']), f, indent=2)

        print(f"Success: Saved {link['player']} → {len(salary_data)} years")
        time.sleep(4)  # Be nice

    print("All done!")

# async def churn() -> None:
#     """Main function to scrape salary data from all player links"""
#     headers = create_http_headers()
#     connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
#     timeout = aiohttp.ClientTimeout(total=30, connect=10)
   
#     cookies = {"cf_clearance": CF_CLEARANCE_VALUE}

#     async with aiohttp.ClientSession(headers=headers, cookies=cookies, connector=connector, timeout=timeout) as session:
#         with open("unique_links.json", 'r') as f:
#             unique_links = json.load(f)
       
#         existing_salaries = []
#         try:
#             with open("salaries.json", 'r') as f:
#                 existing_salaries = json.load(f)
#         except FileNotFoundError:
#             print("No existing salaries.json found, starting fresh.")
       
#         existing_ids = {entry['id'] for entry in existing_salaries if entry.get('salaries')}
#         remaining_links = [link for link in unique_links if link['id'] not in existing_ids]
       
#         print(f"Total unique links: {len(unique_links)}")
#         print(f"Already processed: {len(existing_ids)}")
#         print(f"Remaining to process: {len(remaining_links)}")
       
#         if not remaining_links:
#             print("All links have been processed!")
#             return
       
#         salaries_by_id = {entry['id']: entry for entry in existing_salaries}
       
#         BIN_SIZE = 1
#         for i in range(0, len(remaining_links), BIN_SIZE):
#             bin_links = remaining_links[i:i + BIN_SIZE]
#             print(f"\nProcessing bin {i // BIN_SIZE + 1}...")
           
#             tasks = [scrape_salary_from_url(link['url'], session) for link in bin_links]
#             salary_results = await asyncio.gather(*tasks, return_exceptions=True)
           
#             for link, salary_result in zip(bin_links, salary_results):
#                 if isinstance(salary_result, Exception):
#                     print(f"Error processing {link['url']}: {salary_result}")
#                     salary_dict = {}
#                 else:
#                     salary_dict = salary_result
               
#                 entry = {
#                     "id": link['id'],
#                     "player": link['player'],
#                     "salaries": salary_dict
#                 }
#                 salaries_by_id[link['id']] = entry
           
#             all_salaries = list(salaries_by_id.values())
#             all_salaries.sort(key=lambda x: x['id'])
           
#             with open("salaries.json", 'w') as f:
#                 json.dump(all_salaries, f, indent=2)
           
#             print(f"Saved progress. Total entries: {len(all_salaries)}")
#             await asyncio.sleep(4)
       
#         print(f"\nChurn complete! All salary data saved to salaries.json")


if __name__ == "__main__":
    # Uncomment to extract unique links from CSV
    # extract_unique_links("players.csv", "unique_links.json")
   
    # Uncomment to test single scrape
    # async def test_single_scrape():
    #     async with aiohttp.ClientSession(headers=create_http_headers()) as session:
    #         result = await scrape_salary_from_url("https://www.baseball-reference.com/players/l/lindofr01.shtml", session)
    #         print(result)
    # asyncio.run(test_single_scrape())
   
    # Uncomment to run full scraping
    asyncio.run(churn_with_cloudscraper())
