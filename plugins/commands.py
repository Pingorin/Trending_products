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
    msg = await message.reply_text("🔎 Amazon Bestsellers ki photos nikal raha hu...")
    data = await get_amazon_trending()
    
    # Agar error/screenshot aaya
    if data and isinstance(data[0], str) and "SCREENSHOT_SAVED" in data[0]:
        if os.path.exists("amazon_error.png"):
            await message.reply_photo(photo="amazon_error.png", caption="⚠️ Layout issue")
            os.remove("amazon_error.png")
        await msg.delete()
        return

    if not data or (isinstance(data[0], str) and "Error" in data[0]):
        await msg.edit_text("❌ Kuch nahi mila ya scraper fail ho gaya.")
        return

    # Loading message delete karo
    await msg.delete()
    
    # Har product ko alag photo message ke tarah bhejo
    for item in data:
        caption_text = f"🔥 **Trending on Amazon**\n\n📦 **Name:** {item['name']}\n💰 **Price:** {item['price']}\n🔗 **Link:** [Click Here]({item['link']})"
        try:
            await client.send_photo(
                chat_id=message.chat.id,
                photo=item['image'],
                caption=caption_text
            )
        except Exception:
            # Agar image URL kharab ho, toh sirf text bhej do
            await client.send_message(chat_id=message.chat.id, text=caption_text, disable_web_page_preview=False)

# ... (Niche Flipkart aur Meesho ka purana code waise hi rehne dein)
