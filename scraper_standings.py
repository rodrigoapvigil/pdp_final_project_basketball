import csv
import requests
from lxml import html
import ssl
import urllib3

class CustomHttpAdapter(requests.adapters.HTTPAdapter):
    """Adapter to modify the SSL context of requests, helping bypass simple TLS fingerprinting."""
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().proxy_manager_for(*args, **kwargs)

def fetch_html(url: str) -> bytes:
    """Fetch the HTML content of the specified URL."""
    ctx = urllib3.util.ssl_.create_urllib3_context()
    ctx.set_ciphers('DEFAULT@SECLEVEL=1:HIGH:!DH:!aNULL')
    ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

    session = requests.Session()
    session.mount('https://', CustomHttpAdapter(ssl_context=ctx))
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    response = session.get(url)
    response.raise_for_status()
    return response.content

def parse_standings(html_content: bytes) -> list:
    """Extract NBA active franchises data using XPath."""
    tree = html.fromstring(html_content)
    standings = []
    
    # Locate table rows in active franchises table, ignoring header rows
    rows = tree.xpath('//table[contains(@id, "teams_active")]/tbody/tr[not(contains(@class, "thead"))]')
    
    for row in rows:
        # Extract required columns from table cells
        team = row.xpath('.//th[@data-stat="franch_name"]//text()') or row.xpath('.//td[@data-stat="franch_name"]//text()')
        games = row.xpath('.//td[@data-stat="g"]//text()')
        wins = row.xpath('.//td[@data-stat="wins"]//text()')
        losses = row.xpath('.//td[@data-stat="losses"]//text()')
        win_loss_pct = row.xpath('.//td[@data-stat="win_loss_pct"]//text()')
        playoffs = row.xpath('.//td[@data-stat="years_playoffs"]//text()')
        champs = row.xpath('.//td[@data-stat="years_league_champion"]//text()')
        
        # Clean and append data if primary elements are found
        if team and games and wins and losses:
            clean_team = ''.join(team).strip()
            clean_team = clean_team.replace('*', '').strip() 
            
            standings.append({
                'Franchise': clean_team,
                'G': games[0].strip() if games else '0',
                'W': wins[0].strip() if wins else '0',
                'L': losses[0].strip() if losses else '0',
                'W/L%': win_loss_pct[0].strip() if win_loss_pct else '0.000',
                'Plyfs': playoffs[0].strip() if playoffs else '0',
                'Champ': champs[0].strip() if champs else '0'
            })
            
    return standings

def save_to_csv(data: list, filepath: str) -> None:
    """Write extracted data to a CSV file."""
    if not data:
        return

    keys = ['Franchise', 'G', 'W', 'L', 'W/L%', 'Plyfs', 'Champ']
    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

def main():
    """Main entrypoint of the scraper script."""
    url = 'https://www.basketball-reference.com/teams/'
    csv_filename = 'standings.csv'
    
    try:
        html_content = fetch_html(url)
        standings = parse_standings(html_content)
        
        if standings:
            save_to_csv(standings, csv_filename)
        else:
            print("No standings data found.")
            
    except Exception as e:
        print(f"Error during scraping: {e}")

if __name__ == '__main__':
    main()
