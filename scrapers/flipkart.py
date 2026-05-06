import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def get_flipkart_trending():
    url = "https://www.flipkart.com/search?q=trending+products&sort=popularity"
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
            
            items = soup.find_all("div", class_="_1AtVbE", limit=5)
            for item in items:
                name_tag = item.find("a", class_="IRpwT")
                price_tag = item.find("div", class_="_30jeq3")
                link_tag = item.find("a", class_="_2Uzu97")
                if name_tag and link_tag:
                    name = name_tag.text.strip()
                    price = price_tag.text.strip() if price_tag else 'N/A'
                    link = f"https://www.flipkart.com{link_tag['href']}"
                    products.append(f"📦 **{name}**\n💰 {price}\n🔗 [View on Flipkart]({link})")
        except Exception as e:
            products.append(f"⚠️ Flipkart Error: {str(e)}")
        finally:
            await browser.close()
    return products
