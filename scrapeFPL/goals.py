from playwright.async_api import async_playwright
import asyncio
from playwright_stealth import stealth_async

async def scrape_fpl() -> list:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await stealth_async(page)
        
        # Load the initial page to establish the session
        await page.goto("https://www.premierleague.com/stats/top/players/goals")
        await page.wait_for_load_state('networkidle')  # Wait for everything to load

        all_data = []
        page_number = 1
        page_size = 10

        # Custom headers as seen in the request
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Dnt": "1",
            "Origin": "https://www.premierleague.com",
            "Referer": "https://www.premierleague.com/",
            "Sec-Ch-Ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            # Add any additional headers here if necessary
        }

        while True:
            # Construct the API URL with the current page number
            api_url = f"https://footballapi.pulselive.com/football/stats/ranked/players/goals?page={page_number}&pageSize={page_size}&compSeasons=719&comps=1&compCodeForActivePlayer=EN_PR&altIds=true"
            
            # Use Playwright's context to fetch the API data with headers
            response = await page.request.get(api_url, headers=headers)
            if response.status != 200:
                print(f"Failed to fetch page {page_number}, status code {response.status}")
                break

            data = await response.json()
            stats = data.get('stats', [])

            if not stats:
                print("No more data to fetch.")
                break

            # print (stats)

            stats = stats['content']
            for player_data in stats:
                owner = player_data['owner']
    
                # Extract the necessary fields
                player_row = {
                    'Player ID': owner.get('playerId'),
                    'Name': owner['name'].get('display'),
                    'First Name': owner['name'].get('first'),
                    'Last Name': owner['name'].get('last'),
                    'Position': owner['info'].get('position'),
                    'Shirt Number': owner['info'].get('shirtNum'),
                    'Position Info': owner['info'].get('positionInfo'),
                    'Current Team': owner['currentTeam'].get('name'),
                    'Team Abbreviation': owner['currentTeam']['club'].get('abbr'),
                    'Goals': player_data.get('value'),
                    'Age': owner.get('age'),
                    'Birth Date': owner['birth']['date'].get('label'),
                    'Birth Place': owner['birth'].get('place'),
                    'Nationality': owner['nationalTeam'].get('country'),
                    'Rank': player_data.get('rank'),
                }
    
                all_data.append(player_row)

            print(f"Page {page_number} data:", stats)

            # Check if there are more pages of data
            if len(stats) < page_size:
                print("Reached the last page.")
                break

            # Increment the page number for the next iteration
            page_number += 1

        await browser.close()
        return all_data

if __name__ == '__main__':
    data = asyncio.run(scrape_fpl())
    for player in data:
        print(player)
