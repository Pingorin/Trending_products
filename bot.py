from pyrogram import Client
from fastapi import FastAPI
import info  # Nayi info.py file ko import kiya

# --- Client Setup (Plugins connect karna aur info.py se data lena) ---
app = FastAPI()

bot = Client(
    "ScraperBot", 
    api_id=info.API_ID, 
    api_hash=info.API_HASH, 
    bot_token=info.BOT_TOKEN,
    plugins=dict(root="plugins") # Ye line saare commands auto-load karegi
)

# --- FastAPI Server ---
@app.get("/")
def home():
    return {"status": "Modular Playwright Scraper is running with Info.py!"}

@app.on_event("startup")
async def startup():
    await bot.start()
    print("Bot started successfully with credentials from info.py!")
