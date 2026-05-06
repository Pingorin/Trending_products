import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def get_meesho_trending():
    url = "https://www.meesho.com/search?q=trending"
    products = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(3)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            items = soup.find_all("div", class_="ProductList__GridCol-sc-89n981-0", limit=5)
            for item in items:
                name_tag = item.find("p", class_="ShippingStatus__StyledP-sc-1buon6a-0")
                price_tag = item.find("h5", class_="Heading__StyledH5-sc-1m99f8x-0")
                if name_tag:
                    name = name_tag.text.strip()
                    price = price_tag.text.strip() if price_tag else 'N/A'
                    products.append(f"📦 **{name}**\n💰 {price}\n🛒 Platform: Meesho")
        except Exception as e:
            products.append(f"⚠️ Meesho Error: {str(e)}")
        finally:
            await browser.close()
    return products
