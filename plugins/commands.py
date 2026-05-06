import os
from pyrogram import Client, filters
from scrapers.amazon import get_amazon_trending
from scrapers.flipkart import get_flipkart_trending
from scrapers.meesho import get_meesho_trending

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply_text("Bot is live! Commands:\n/amazon\n/flipkart\n/meesho")

@Client.on_message(filters.command("amazon") & filters.private)
async def amazon_cmd(client, message):
    msg = await message.reply_text("🔎 Amazon Bestsellers check kar raha hu...")
    data = await get_amazon_trending()
    
    # Check agar scraper ne screenshot signal bheja hai
    if data and "SCREENSHOT_SAVED" in data:
        if os.path.exists("amazon_error.png"):
            await message.reply_photo(
                photo="amazon_error.png",
                caption="⚠️ Amazon ne data nahi diya. Is photo me dekho kya dikh raha hai (Captcha ya Block?)"
            )
            os.remove("amazon_error.png") # Delete after sending
            await msg.delete()
        else:
            await msg.edit_text("❌ Data nahi mila aur screenshot bhi fail ho gaya.")
        return

    response = "\n\n---\n\n".join(data) if data else "Kuch nahi mila."
    await msg.edit_text(f"🔥 **Amazon Top Trending:**\n\n{response}", disable_web_page_preview=True)

# Flipkart aur Meesho ke commands niche wese hi rakhein...
