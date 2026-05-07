import os
from pyrogram import Client, filters
from scrapers.amazon import get_amazon_data

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply_text("Bot is live! Commands:\n/mostsold\n/trending\n/flipkart\n/meesho")

# Commands unchanged
@Client.on_message(filters.command("mostsold") & filters.private)
async def mostsold_cmd(client, message):
    msg = await message.reply_text("🔎 Amazon Bestsellers nikal raha hu...")
    data = await get_amazon_data("bestsellers")
    await send_products(client, message, msg, data, "🏆 Most Sold on Amazon")

@Client.on_message(filters.command("trending") & filters.private)
async def trending_cmd(client, message):
    msg = await message.reply_text("🔎 Amazon Trending products nikal raha hu...")
    data = await get_amazon_data("trending")
    await send_products(client, message, msg, data, "🚀 Hot Trending on Amazon")

# Better error checking
async def send_products(client, message, msg, data, title):
    if not data or not isinstance(data, list) or len(data) == 0:
        await msg.edit_text("❌ Kuch nahi mila ya scraper fail ho gaya.")
        return

    # Check for screenshot signal or explicit error string
    if isinstance(data[0], str):
        if "SCREENSHOT_SAVED" in data[0]:
            await msg.edit_text("❌ Layout issue ya block. Bot text nahi padh paaya.")
        else:
            await msg.edit_text(data[0]) # Show explicit error message
        return

    # Delete loading msg if everything is fine
    await msg.delete()
    
    # Send photo messages
    for item in data:
        caption_text = f"**{title}**\n\n📦 **Name:** {item['name']}\n💰 **Price:** {item['price']}\n🔗 **Link:** [Click Here]({item['link']})"
        try:
            await client.send_photo(chat_id=message.chat.id, photo=item['image'], caption=caption_text)
        except Exception:
            await client.send_message(chat_id=message.chat.id, text=caption_text, disable_web_page_preview=False)
