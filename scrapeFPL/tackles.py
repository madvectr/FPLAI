import aiohttp
import asyncio
import csv

async def fetch_data_for_season(session, comp_season_id, season_name):
    all_data = []
    page_number = 0
    page_size = 10

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
    }

    while True:
        api_url = f"https://footballapi.pulselive.com/football/stats/ranked/players/total_tackle?page={page_number}&pageSize={page_size}&compSeasons={comp_season_id}&comps=1&compCodeForActivePlayer=EN_PR&altIds=true"

        async with session.get(api_url, headers=headers) as response:
            if response.status != 200:
                print(f"Failed to fetch page {page_number} for season {season_name}, status code {response.status}")
                break

            data = await response.json()
            print(data)
            stats = data.get('stats', {}).get('content', [])
            print(stats)

            if not stats:
                print(f"No more data to fetch for season {season_name}.")
                break

            # Processing the JSON data into rows
            for player_data in stats:
                owner = player_data['owner']
                
                player_row = {
                    'Season': season_name,
                    'Player ID': owner.get('playerId', 'n/a'),
                    'Name': owner['name'].get('display', 'n/a'),
                    'First Name': owner['name'].get('first', 'n/a'),
                    'Last Name': owner['name'].get('last', 'n/a'),
                    'Position': owner['info'].get('position', 'n/a'),
                    'Shirt Number': owner['info'].get('shirtNum', 'n/a'),
                    'Position Info': owner['info'].get('positionInfo', 'n/a'),
                    'Current Team': owner.get('currentTeam', {}).get('name', 'n/a'),
                    'Team Abbreviation': owner.get('currentTeam', {}).get('club', {}).get('abbr', 'n/a'),
                    'TotalTackles': player_data.get('value', '-1'),
                    'Age': owner.get('age', '-1'),
                    'Nationality': owner['nationalTeam'].get('country'),
                    'Rank': player_data.get('rank'),
                }
                
                all_data.append(player_row)

            print(f"Page {page_number} data for season {season_name}: {len(stats)} players processed.")

            # Check if there are more pages of data
            if len(stats) < page_size:
                print(f"Reached the last page for season {season_name}.")
                break

            # Increment the page number for the next iteration
            page_number += 1

    return all_data

async def save_to_csv(data, filename='data/totaltackles.csv'):
    # Specify the fields for the CSV
    fieldnames = [
        'Season', 'Player ID', 'Name', 'First Name', 'Last Name',
        'Position', 'Shirt Number', 'Position Info', 'Current Team',
        'Team Abbreviation', 'TotalTackles', 'Age', 
        'Nationality', 'Rank'
    ]

    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"Data saved to {filename}")

async def main():
    seasons = [
        {'name': '2024/25', 'id': 719},
        {'name': '2023/24', 'id': 578},
        {'name': '2022/23', 'id': 489},
        {'name': '2021/22', 'id': 418},
        {'name': '2020/21', 'id': 363},
        {'name': '2019/20', 'id': 274},
        {'name': '2018/19', 'id': 210},
        {'name': '2017/18', 'id': 79}
    ]

    all_seasons_data = []

    async with aiohttp.ClientSession() as session:
        for season in seasons:
            print(f"Fetching data for season {season['name']}...")
            season_data = await fetch_data_for_season(session, season['id'], season['name'])
            all_seasons_data.extend(season_data)

    await save_to_csv(all_seasons_data)

if __name__ == '__main__':
    asyncio.run(main())
