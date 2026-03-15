=============================================================================
FINAL PROJECT: PROGRAMMING FOR DATA SCIENCE
=============================================================================

GROUP MEMBERS:
- Mohammed Ahajjam Ziggaf Kanjaa
- Rodrigo Peña Vigil
- Sergio Martínez Lahoz 
- Víctor Ramírez Castaño
- Younes Labvhiri

PROJECT DESCRIPTION:
This project analyzes NBA basketball data, cross-referencing team historical 
performance, player statistics, and player salaries. The project is divided 
into two main parts: Data Collection (Web Scraping) and Data Manipulation 
& Visualization.

PART 1: DATA COLLECTION MODULES (Web Scraping)
We extracted 3 different resources from Basketball-Reference.com using 
static scraping techniques. We implemented a CustomHttpAdapter modifying 
the SSL context to bypass Cloudflare 403 Forbidden errors securely.

- scraper_standings.py: Extracts the historical performance of all active 
  NBA franchises. Generates 'standings.csv'.
- scraper_players.py: Extracts the per-game statistics of all NBA players 
  for the 2024 season. Generates 'players.csv'.
- scraper_salaries.py: Extracts the current season (y1) salaries of NBA 
  players. Generates 'salaries.csv'.

PART 2: DATA MANIPULATION & VISUALIZATION
[To be filled].

PACKAGE DEPENDENCIES:
To run the Web Scraping modules, the following external packages are required:
- requests
- lxml
- urllib3
[To be filled for Part 2].

HOW TO EXECUTE:
1. Ensure all dependencies are installed (pip install requests lxml urllib3).
2. Open a terminal in the project directory.
3. Run the scrapers individually to generate the data:
   > python scraper_standings.py
   > python scraper_players.py
   > python scraper_salaries.py
[To be filled for Part 2].

PRESENTATION LINKS:
- Video Recording Link: [Add link here]
- Presentation Slides: The slides used for the video are included in the 
  submission zip file as 'slides.pdf'.