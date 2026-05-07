import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def get_amazon_data(list_type="bestsellers"):
    # URL Selection (Same logic)
    if list_type == "bestsellers":
        url = "https://www.amazon.in/gp/bestsellers"
    elif list_type == "trending":
        url = "https://www.amazon.in/gp/movers-and-shakers"
        
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
            if not cards: cards = soup.find_all("div", id="gridItemRoot")
            if not cards: cards = soup.find_all("div", class_="zg-grid-general-faceout")

            if not cards:
                return ["SCREENSHOT_SAVED"]

            for card in cards:
                if len(products) >= 5: break
                    
                a_tags = card.find_all("a", href=True)
                link = None
                for a in a_tags:
                    if "amazon.in" in a['href'] or a['href'].startswith('/'):
                        link = f"https://www.amazon.in{a['href']}" if a['href'].startswith('/') else a['href']
                        break
                if not link: continue

                # --- SUPER PRECISE PHOTO & NAME FINDER ---
                image_url = "https://via.placeholder.com/400x400.png?text=No+Image"
                name = ""
                
                # specific photo container ko target karna (zg-div-img-card)
                # agar wo na mile to general finder use karna
                image_container = card.find("div", class_="zg-div-img-card") or card.find("div", class_="a-img-container")
                
                if image_container:
                    img_tag = image_container.find("img")
                    if img_tag and img_tag.get('src') and 'media-amazon' in img_tag['src']:
                        image_url = img_tag['src']
                        if img_tag.get('alt'):
                            name = img_tag['alt']
                
                # photo fail hone par fallback
                if image_url == "https://via.placeholder.com/400x400.png?text=No+Image":
                    # pure dabbe me koi bhi real product photo dhoondho (skip icons)
                    for img in card.find_all("img"):
                        src = img.get('src', '')
                        alt = img.get('alt', '')
                        if 'media-amazon' in src and "arrow" not in alt.lower():
                            image_url = src
                            if alt: name = alt
                            break

                # agar naam abhi bhi 'increased' wala hai, to text div se naam nikal lo
                if "increased" in name.lower() or "arrow" in name.lower():
                    text_tags = card.find_all("div", class_="p13n-sc-truncate") or card.find_all("div", class_="_cDEzb_p13n-sc-css-line-clamp-3_g3ie1")
                    if text_tags:
                        name = text_tags[0].text.strip()
                    else:
                        name = "Amazon Trending Product" # fallback

                # Format short title
                short_name = (name[:75] + '...') if len(name) > 75 else name

                # --- SUPER PRECISE PRICE FINDER ---
                price = "N/A"
                price_container = card.find("span", class_="p13n-sc-price") or card.find("span", class_="a-price-whole")
                if price_container:
                    price = price_container.text.strip()
                    if '₹' not in price: price = "₹" + price
                else:
                    # broad search based on rupee symbol ₹ (Movers logic)
                    price_texts = card.find_all(string=lambda t: t and '₹' in t)
                    if price_texts: price = price_texts[0].strip()
                
                products.append({
                    "name": short_name,
                    "price": price,
                    "link": link,
                    "image": image_url
                })
                    
            if not products:
                return ["SCREENSHOT_SAVED"]

        except Exception as e:
            products.append(f"⚠️ Amazon Error: {str(e)}")
        finally:
            await browser.close()
            
    return products
