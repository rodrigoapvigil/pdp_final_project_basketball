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

def parse_players(html_content: bytes) -> list:
    """Extract NBA per game player stats using XPath."""
    tree = html.fromstring(html_content)
    players = []
    
    # Locate table rows in per_game stats table, ignoring header rows
    rows = tree.xpath('//table[@id="per_game_stats"]/tbody/tr[not(contains(@class, "thead"))]')
    
    stat_mapping = {
        'player': 'name_display',
        'pos': 'pos',
        'age': 'age',
        'team_id': 'team_name_abbr',
        'g': 'games',
        'mp': 'mp_per_g',
        'pts': 'pts_per_g',
        'trb': 'trb_per_g',
        'ast': 'ast_per_g',
        'fg_pct': 'fg_pct',
        'fg3_pct': 'fg3_pct',
        'efg_pct': 'efg_pct',
        'stl': 'stl_per_g',
        'blk': 'blk_per_g',
        'tov': 'tov_per_g'
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
            
            # Handle empty values setting them to '0.0' for all mostly numeric attributes
            if not clean_val:
                if out_stat in ['player', 'pos', 'team_id']:
                    clean_val = ''
                else:
                    clean_val = '0.0'
                    
            player_data[out_stat] = clean_val
            
            if out_stat == 'player' and clean_val:
                has_player = True
                
        if has_player:
            players.append(player_data)
            
    return players

def save_to_csv(data: list, filepath: str) -> None:
    """Write extracted data to a CSV file."""
    if not data:
        return

    keys = ['player', 'pos', 'age', 'team_id', 'g', 'mp', 'pts', 'trb', 'ast', 'fg_pct', 'fg3_pct', 'efg_pct', 'stl', 'blk', 'tov']
    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

def main():
    """Main entrypoint of the scraper script."""
    url = 'https://www.basketball-reference.com/leagues/NBA_2024_per_game.html'
    csv_filename = 'players.csv'
    
    try:
        html_content = fetch_html(url)
        players = parse_players(html_content)
        
        if players:
            save_to_csv(players, csv_filename)
            print(f"Successfully saved {len(players)} players to {csv_filename}")
        else:
            print("No players data found.")
            
    except Exception as e:
        print(f"Error during scraping: {e}")

if __name__ == '__main__':
    main()
