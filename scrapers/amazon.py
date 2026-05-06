import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def get_amazon_trending():
    url = "https://www.amazon.in/gp/bestsellers"
    products = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(4) 
            await page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(2)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Smart Tag Finder: Hum multiple layouts check karenge
            cards = soup.find_all("li", class_="a-carousel-card") # Naya layout (jo photo me hai)
            if not cards:
                cards = soup.find_all("div", id="gridItemRoot")
            if not cards:
                cards = soup.find_all("div", class_="zg-grid-general-faceout") # Purana layout

            # Agar ab bhi nahi mila toh screenshot le lo
            if not cards:
                await page.screenshot(path="amazon_error.png")
                return ["SCREENSHOT_SAVED"]

            # Top 5 unique products nikalenge
            for card in cards:
                if len(products) >= 5: # Sirf top 5 chahiye
                    break
                    
                # Link nikalna
                link_tag = card.find("a", class_="a-link-normal")
                if not link_tag or 'href' not in link_tag.attrs:
                    continue
                
                link = f"https://www.amazon.in{link_tag['href']}" if not link_tag['href'].startswith('http') else link_tag['href']
                
                # Name nikalna (Image ke alt text ya div se)
                name = ""
                img_tag = card.find("img")
                name_div = card.find("div", class_="_cDEzb_p13n-sc-css-line-clamp-3_g3ie1") or card.find("div", class_="p13n-sc-truncate")
                
                if name_div:
                    name = name_div.text.strip()
                elif img_tag and img_tag.get('alt'):
                    name = img_tag['alt']
                    
                if not name:
                    continue
                    
                # Price nikalna
                price_tag = card.find("span", class_="p13n-sc-price") or card.find("span", class_="a-price-whole")
                price = price_tag.text.strip() if price_tag else 'N/A'
                
                # Format karke list me dalna
                product_info = f"📦 **{name[:60]}...**\n💰 {price}\n🔗 [View on Amazon]({link})"
                if product_info not in products: # Duplicate rokne ke liye
                    products.append(product_info)
                    
        except Exception as e:
            products.append(f"⚠️ Amazon Error: {str(e)}")
        finally:
            await browser.close()
            
    return products
