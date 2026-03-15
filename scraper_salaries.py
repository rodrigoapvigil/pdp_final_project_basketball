import csv
import ssl
import requests
from lxml import html
from requests.adapters import HTTPAdapter
import urllib3

class CustomHttpAdapter (HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)

def fetch_html(url: str) -> bytes:
    """Fetch HTML content from a URL, bypassing Cloudflare 403 errors."""
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    ctx.set_ciphers('DEFAULT@SECLEVEL=1:HIGH:!DH:!aNULL')

    session = requests.session()
    session.mount('https://', CustomHttpAdapter(ctx))
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    response = session.get(url, headers=headers)
    response.raise_for_status()
    return response.content

def parse_salaries(html_content: bytes) -> list:
    """Extract NBA player salaries using XPath."""
    tree = html.fromstring(html_content)
    salaries = []
    
    # Locate table rows in player-contracts stats table, ignoring header rows
    rows = tree.xpath('//table[@id="player-contracts"]/tbody/tr[not(contains(@class, "thead"))]')
    
    stat_mapping = {
        'player': 'player',
        'team_id': 'team_id',
        'y1': 'y1'
    }
    
    for row in rows:
        player_data = {}
        has_player = False
        
        for out_stat, html_stat in stat_mapping.items():
            # Extract the text specifically within the relevant cell
            val = row.xpath(f'.//*[@data-stat="{html_stat}"]//text()')
            clean_val = ''.join(val).strip() if val else ''
            
            # Clean asterisk from player names that indicate Hall of Fame or similar
            if out_stat == 'player':
                clean_val = clean_val.replace('*', '').strip()
            
            # Clean salary
            if out_stat == 'y1':
                if clean_val:
                    clean_val = clean_val.replace('$', '').replace(',', '').strip()
                else:
                    clean_val = '0'
                    
            if not clean_val and out_stat != 'y1':
                clean_val = ''
                    
            player_data[out_stat] = clean_val
            
            if out_stat == 'player' and clean_val:
                has_player = True
                
        if has_player:
            salaries.append(player_data)
            
    return salaries

def save_to_csv(data: list, filename: str):
    """Save a list of dictionaries to a CSV file."""
    if not data:
        print(f"No data to save for {filename}")
        return

    keys = ['player', 'team_id', 'y1']
    
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    print(f"Successfully saved {len(data)} rows to {filename}")

def main():
    target_url = 'https://www.basketball-reference.com/contracts/players.html'
    output_filename = 'salaries.csv'

    try:
        print(f"Fetching data from {target_url}...")
        html_content = fetch_html(target_url)
        
        print(f"Parsing salaries data...")
        salaries_data = parse_salaries(html_content)
        
        if salaries_data:
            print(f"Saving to {output_filename}...")
            save_to_csv(salaries_data, output_filename)
        else:
            print("No salaries data found.")
            
    except Exception as e:
        print(f"Error during scraping: {e}")

if __name__ == '__main__':
    main()
