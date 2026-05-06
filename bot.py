import os
import asyncio
import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pymongo import MongoClient
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- Credentials ---
API_ID = "20638104"  # Apna Telegram API ID dalein
API_HASH = "6c884690ca85d39a4c5ad7c15b194e42" # Apna API Hash dalein
BOT_TOKEN = "8782883934:AAFkE-O0JCkLIWYmAfhVVxbY5hZoR24t3vI"
MONGO_URI = "YOUR_MONGODB_URI"
OWNER_ID = 7245547751  # Apna Telegram User ID dalein jahan message chahiye

# --- Database Setup ---
db_client = MongoClient(MONGO_URI)
db = db_client["TrendingBot"]
collection = db["products"]

# --- Clients Init ---
app = FastAPI()
bot = Client("ScraperBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- Scraping Logic (Amazon Bestsellers Skeleton) ---
def scrape_amazon_trending():
    # Headers zaroori hain taaki Amazon block na kare
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    url = "https://www.amazon.in/gp/bestsellers"
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # NOTE: Amazon ka HTML structure change hota rehta hai, yeh ek generic example hai
        items = soup.find_all("div", class_="zg-grid-general-faceout")
        
        new_products = []
        for item in items[:5]: # Top 5 products
            link_tag = item.find("a", class_="a-link-normal")
            if link_tag:
                link = "https://www.amazon.in" + link_tag['href']
                # Product ID extract karein URL se
                product_id = link.split("/dp/")[1].split("/")[0] if "/dp/" in link else link_tag['href']
                
                # Check agar MongoDB mein pehle se hai
                if not collection.find_one({"_id": product_id}):
                    name_tag = item.find("div", class_="_cDEzb_p13n-sc-css-line-clamp-3_g3ie1")
                    price_tag = item.find("span", class_="p13n-sc-price")
                    
                    product = {
                        "_id": product_id,
                        "name": name_tag.text.strip() if name_tag else "Unknown Name",
                        "price": price_tag.text.strip() if price_tag else "Unknown Price",
                        "link": link,
                        "platform": "Amazon"
                    }
                    collection.insert_one(product)
                    new_products.append(product)
                    
        return new_products
    except Exception as e:
        print(f"Scraping Error: {e}")
        return []

# --- Auto Sender Task ---
async def check_and_send():
    print("Checking for new trending products...")
    new_items = scrape_amazon_trending()
    
    for item in new_items:
        msg = f"🔥 **New Trending Product!** 🔥\n\n" \
              f"🛒 **Platform:** {item['platform']}\n" \
              f"📦 **Name:** {item['name']}\n" \
              f"💰 **Price:** {item['price']}\n" \
              f"🔗 [Click Here to View]({item['link']})"
        
        try:
            await bot.send_message(chat_id=OWNER_ID, text=msg, disable_web_page_preview=False)
            await asyncio.sleep(2) # Flood wait se bachne ke liye delay
        except Exception as e:
            print(f"Telegram Send Error: {e}")

# --- FastAPI Routes & Events ---
@app.get("/")
def home():
    return {"status": "Bot is running perfectly on Hugging Face Spaces!"}

@app.on_event("startup")
async def startup_event():
    # Bot ko background mein start karna
    await bot.start()
    print("Bot Started!")
    
    # Scheduler set karna jo har 2 ghante mein scraping kare
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_and_send, "interval", hours=2)
    scheduler.start()
