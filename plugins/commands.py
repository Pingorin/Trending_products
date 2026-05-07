import os
from pyrogram import Client, filters
# Naya function import kiya
from scrapers.amazon import get_amazon_data

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply_text("Bot is live! Commands:\n/mostsold (Sabse zyada bikne wale)\n/trending (Aaj ke trending)\n/flipkart\n/meesho")

# --- MOST SOLD COMMAND ---
@Client.on_message(filters.command("mostsold") & filters.private)
async def mostsold_cmd(client, message):
    msg = await message.reply_text("🔎 Amazon Bestsellers nikal raha hu...")
    # 'bestsellers' type pass kiya
    data = await get_amazon_data("bestsellers")
    await send_products(client, message, msg, data, "🏆 Most Sold on Amazon")

# --- TRENDING COMMAND ---
@Client.on_message(filters.command("trending") & filters.private)
async def trending_cmd(client, message):
    msg = await message.reply_text("🔎 Amazon Movers & Shakers (Trending) nikal raha hu...")
    # 'trending' type pass kiya
    data = await get_amazon_data("trending")
    await send_products(client, message, msg, data, "🚀 Hot Trending on Amazon")

# Message bhejne ka common function (code chota rakhne ke liye)
async def send_products(client, message, msg, data, title):
    if data and isinstance(data[0], str) and "SCREENSHOT_SAVED" in data[0]:
        await msg.edit_text("❌ Layout issue ya block. Bot text nahi padh paaya.")
        return

    if not data or (isinstance(data[0], str) and "Error" in data[0]):
        await msg.edit_text("❌ Kuch nahi mila ya scraper fail ho gaya.")
        return

    await msg.delete()
    
    for item in data:
        caption_text = f"**{title}**\n\n📦 **Name:** {item['name']}\n💰 **Price:** {item['price']}\n🔗 **Link:** [Click Here]({item['link']})"
        try:
            await client.send_photo(chat_id=message.chat.id, photo=item['image'], caption=caption_text)
        except Exception:
            await client.send_message(chat_id=message.chat.id, text=caption_text, disable_web_page_preview=False)
