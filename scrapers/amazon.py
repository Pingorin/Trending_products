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
            
            # Cards dhoondhna
            cards = soup.find_all("li", class_="a-carousel-card")
            if not cards:
                cards = soup.find_all("div", id="gridItemRoot")
            if not cards:
                cards = soup.find_all("div", class_="zg-grid-general-faceout")

            if not cards:
                await page.screenshot(path="amazon_error.png")
                return ["SCREENSHOT_SAVED"]

            # Super-Smart Extraction Logic
            for card in cards:
                if len(products) >= 5:
                    break
                    
                # 1. Link dhoondhna (koi bhi valid a-tag)
                a_tags = card.find_all("a", href=True)
                link = None
                for a in a_tags:
                    if "amazon.in" in a['href'] or a['href'].startswith('/'):
                        link = f"https://www.amazon.in{a['href']}" if a['href'].startswith('/') else a['href']
                        break
                
                if not link:
                    continue
                    
                # 2. Name dhoondhna (Image ka alt tag kabhi fail nahi hota)
                name = ""
                img_tag = card.find("img")
                if img_tag and img_tag.get('alt'):
                    name = img_tag['alt']
                else:
                    name = "Trending Product" # Agar naam nahi mila
                    
                # 3. Price dhoondhna (Direct Rupee '₹' symbol ko catch karna)
                price = "N/A"
                rupee_texts = card.find_all(string=lambda t: t and '₹' in t)
                if rupee_texts:
                    price = rupee_texts[0].strip()
                else:
                    price_tag = card.find("span", class_="a-price-whole")
                    if price_tag:
                        price = "₹" + price_tag.text.strip()
                
                # Title ko thoda chota karna taki message sundar dikhe
                short_name = (name[:60] + '...') if len(name) > 60 else name
                
                product_info = f"📦 **{short_name}**\n💰 {price}\n🔗 [View on Amazon]({link})"
                if product_info not in products:
                    products.append(product_info)
                    
            # Agar extraction fail hota hai, toh screenshot bhej do
            if not products:
                await page.screenshot(path="amazon_error.png")
                return ["SCREENSHOT_SAVED"]

        except Exception as e:
            products.append(f"⚠️ Amazon Error: {str(e)}")
        finally:
            await browser.close()
            
    return products
