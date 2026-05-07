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
            
            cards = soup.find_all("li", class_="a-carousel-card")
            if not cards: cards = soup.find_all("div", id="gridItemRoot")
            if not cards: cards = soup.find_all("div", class_="zg-grid-general-faceout")

            if not cards:
                await page.screenshot(path="amazon_error.png")
                return ["SCREENSHOT_SAVED"]

            for card in cards:
                if len(products) >= 5: break
                    
                # 1. Link nikalna
                a_tags = card.find_all("a", href=True)
                link = None
                for a in a_tags:
                    if "amazon.in" in a['href'] or a['href'].startswith('/'):
                        link = f"https://www.amazon.in{a['href']}" if a['href'].startswith('/') else a['href']
                        break
                if not link: continue

                # 2. Image URL nikalna
                image_url = "https://via.placeholder.com/400x400.png?text=No+Image"
                img_tag = card.find("img")
                name = ""
                
                if img_tag:
                    if img_tag.get('src') and 'media-amazon' in img_tag['src']:
                        image_url = img_tag['src']
                    if img_tag.get('alt'):
                        name = img_tag['alt']

                # 3. Agar image ke 'alt' me naam nahi mila, toh text extract karo
                if not name or name == "Trending Product":
                    texts = [t.strip() for t in card.stripped_strings if len(t.strip()) > 15 and '₹' not in t]
                    if texts:
                        name = texts[0]
                    else:
                        name = "Amazon Trending Product"

                # 4. Price nikalna
                price = "N/A"
                rupee_texts = card.find_all(string=lambda t: t and '₹' in t)
                if rupee_texts:
                    price = rupee_texts[0].strip()
                else:
                    price_tag = card.find("span", class_="a-price-whole")
                    if price_tag:
                        price = "₹" + price_tag.text.strip()
                
                # Dictionary format me save karna taki bot photo bhej sake
                products.append({
                    "name": name[:75] + '...' if len(name) > 75 else name,
                    "price": price,
                    "link": link,
                    "image": image_url
                })
                    
            if not products:
                await page.screenshot(path="amazon_error.png")
                return ["SCREENSHOT_SAVED"]

        except Exception as e:
            products.append(f"⚠️ Amazon Error: {str(e)}")
        finally:
            await browser.close()
            
    return products
