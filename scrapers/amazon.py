import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def get_amazon_trending():
    url = "https://www.amazon.in/gp/bestsellers"
    products = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Naya aur zyada real dikhne wala User-Agent
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(4) # Thoda extra wait taaki pura load ho
            await page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(2)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Amazon ke tags change hote rehte hain, hum broad search use karenge
            items = soup.find_all("div", id="gridItemRoot", limit=5)
            if not items:
                items = soup.find_all("div", class_="zg-grid-general-faceout", limit=5)

            # Agar fir bhi kuch nahi mila, toh screenshot le lo
            if not items:
                await page.screenshot(path="amazon_error.png")
                return ["SCREENSHOT_SAVED"]

            for item in items:
                name_tag = item.find("div", class_="_cDEzb_p13n-sc-css-line-clamp-3_g3ie1")
                price_tag = item.find("span", class_="p13n-sc-price")
                link_tag = item.find("a", class_="a-link-normal")
                
                # Agar naya tag pattern mila
                if not name_tag:
                    name_tag = item.find("div", class_="p13n-sc-truncate")
                    
                if name_tag and link_tag:
                    name = name_tag.text.strip()
                    price = price_tag.text.strip() if price_tag else 'N/A'
                    link = f"https://www.amazon.in{link_tag['href']}"
                    products.append(f"📦 **{name}**\n💰 {price}\n🔗 [View on Amazon]({link})")
                    
        except Exception as e:
            products.append(f"⚠️ Amazon Error: {str(e)}")
        finally:
            await browser.close()
            
    return products
