from playwright.async_api import async_playwright
import asyncio

async def scrape_fpl() -> list:
  async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    # creating new browser context
    context = await browser.new_context()
    # create a new page
    page = await context.new_page()
    # Navigate to FPL
    await page.goto("https://www.premierleague.com/stats/top/players/goals")

    while True:

      table = await page.query_selector('table')
      rows = await table.query_selector_all('tr')

      # Extract data from each row
      data = []
      for row in rows:
        cols = await row.query_selector_all('td')
        row_data = [await col.text_content() for col in cols]
        row_data = [x.strip() for x in row_data]
        data.append(row_data)

      print(data)

      next_pg_btn = await page.query_selector('div.paginationNextContainer')
      print(next_pg_btn)
      classes = await next_pg_btn.get_attribute('class')
      print(classes)
      if 'inactive' in classes:
        break

      # Click on the next page link
      # await page.click('.paginationNextContainer', force=True)
      # await page.keyboard.press('Enter')
      element = await page.query_selector('.paginationNextContainer')
      bounding_box = await element.bounding_box()
      await page.mouse.click(bounding_box['x'] + bounding_box['width'] / 2, bounding_box['y'] + bounding_box['height'] / 2)

      # Wait for the new page to load
      await page.wait_for_load_state('networkidle')


    await browser.close()
    return data

if __name__ == '__main__':
    data = asyncio.run(scrape_fpl())
    print(data)
