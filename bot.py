import os
from pyrogram import Client
from fastapi import FastAPI

# --- Credentials ---
API_ID = "YOUR_API_ID"
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"

# --- Client Setup (Plugins connect karna) ---
app = FastAPI()
bot = Client(
    "ScraperBot", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins") # Ye line saare commands auto-load karegi
)

# --- FastAPI Server ---
@app.get("/")
def home():
    return {"status": "Modular Playwright Scraper is running!"}

@app.on_event("startup")
async def startup():
    await bot.start()
    print("Bot started with plugins successfully!")
