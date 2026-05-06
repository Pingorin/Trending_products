import os
import asyncio
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from fastapi import FastAPI
from playwright.async_api import async_playwright

# --- Credentials ---
API_ID = "20638104"
API_HASH = "6c884690ca85d39a4c5ad7c15b194e42"
BOT_TOKEN = "8782883934:AAFkE-O0JCkLIWYmAfhVVxbY5hZoR24t3vI"

# --- Setup ---
app = FastAPI()
bot = Client("ScraperBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- Playwright Scraping Logic ---
async def scrape_trending(url, platform):
    products = []
    
    # Playwright ko start karna
    async with async_playwright() as p:
        # Headless mode me browser open karna
        browser = await p.chromium.launch(headless=True)
        # Anti-bot bypass karne ke liye real User-Agent set karna
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        
        try:
            # Page par jana aur network idle hone ka wait karna (taki JS load ho jaye)
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Agar bot detect ho gaya toh page reload aur thoda scroll karne ka logic bhi dal sakte hain
            await page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(2) # Page load hone ke liye thoda extra wait
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            if platform == "Amazon":
                items = soup.find_all("div", class_="zg-grid-general-faceout", limit=5)
                for item in items:
                    name_tag = item.find("div", class_="_cDEzb_p13n-sc-css-line-clamp-3_g3ie1")
                    price_tag = item.find("span", class_="p13n-sc-price")
                    link_tag = item.find("a", class_="a-link-normal")
                    if name_tag and link_tag:
                        name = name_tag.text.strip()
                        price = price_tag.text.strip() if price_tag else 'N/A'
                        link = f"https://www.amazon.in{link_tag['href']}"
                        products.append(f"📦 **{name}**\n💰 {price}\n🔗 [View on Amazon]({link})")

            elif platform == "Flipkart":
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

            elif platform == "Meesho":
                # Meesho JS rendering use karta hai, yahan networkidle kaam ayega
                items = soup.find_all("div", class_="ProductList__GridCol-sc-89n981-0", limit=5)
                for item in items:
                    name_tag = item.find("p", class_="ShippingStatus__StyledP-sc-1buon6a-0")
                    price_tag = item.find("h5", class_="Heading__StyledH5-sc-1m99f8x-0")
                    if name_tag:
                        name = name_tag.text.strip()
                        price = price_tag.text.strip() if price_tag else 'N/A'
                        products.append(f"📦 **{name}**\n💰 {price}\n🛒 Platform: Meesho")

        except Exception as e:
            products.append(f"⚠️ Scraping Error on {platform}: {str(e)}")
        finally:
            await browser.close()
            
    return products

# --- Bot Commands ---
@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text(
        "Bot is live! Playwright Backend Loaded 🚀\n\n"
        "Commands:\n"
        "/amazon - Fetch Amazon Trending\n"
        "/flipkart - Fetch Flipkart Popular\n"
        "/meesho - Fetch Meesho Trending"
    )

@bot.on_message(filters.command("amazon") & filters.private)
async def amazon_cmd(client, message):
    msg = await message.reply_text("🔎 Browser khol raha hu, Amazon Bestsellers dhoondne ke liye... (Isme thoda waqt lag sakta hai)")
    url = "https://www.amazon.in/gp/bestsellers"
    data = await scrape_trending(url, "Amazon")
    response = "\n\n---\n\n".join(data) if data else "Kuch nahi mila ya block ho gaye."
    await msg.edit_text(f"🔥 **Amazon Top Trending:**\n\n{response}", disable_web_page_preview=True)

@bot.on_message(filters.command("flipkart") & filters.private)
async def flipkart_cmd(client, message):
    msg = await message.reply_text("🔎 Flipkart par popular products load ho rahe hain...")
    url = "https://www.flipkart.com/search?q=trending+products&sort=popularity"
    data = await scrape_trending(url, "Flipkart")
    response = "\n\n---\n\n".join(data) if data else "Kuch nahi mila."
    await msg.edit_text(f"🔥 **Flipkart Top Trending:**\n\n{response}", disable_web_page_preview=True)

@bot.on_message(filters.command("meesho") & filters.private)
async def meesho_cmd(client, message):
    msg = await message.reply_text("🔎 Meesho ka dynamic data load kar raha hu...")
    url = "https://www.meesho.com/search?q=trending"
    data = await scrape_trending(url, "Meesho")
    response = "\n\n---\n\n".join(data) if data else "Kuch nahi mila."
    await msg.edit_text(f"🔥 **Meesho Top Trending:**\n\n{response}")

# --- FastAPI Setup ---
@app.get("/")
def home():
    return {"status": "Playwright Scraper is running!"}

@app.on_event("startup")
async def startup():
    await bot.start()
