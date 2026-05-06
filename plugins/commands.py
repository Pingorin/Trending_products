from pyrogram import Client, filters
from scrapers.amazon import get_amazon_trending
from scrapers.flipkart import get_flipkart_trending
from scrapers.meesho import get_meesho_trending

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply_text(
        "Bot is live! Modular framework loaded 🚀\n\n"
        "Commands:\n"
        "/amazon - Fetch Amazon Trending\n"
        "/flipkart - Fetch Flipkart Popular\n"
        "/meesho - Fetch Meesho Trending"
    )

@Client.on_message(filters.command("amazon") & filters.private)
async def amazon_cmd(client, message):
    msg = await message.reply_text("🔎 Amazon Bestsellers load kar raha hu...")
    data = await get_amazon_trending()
    response = "\n\n---\n\n".join(data) if data else "Kuch nahi mila ya block ho gaye."
    await msg.edit_text(f"🔥 **Amazon Top Trending:**\n\n{response}", disable_web_page_preview=True)

@Client.on_message(filters.command("flipkart") & filters.private)
async def flipkart_cmd(client, message):
    msg = await message.reply_text("🔎 Flipkart par popular products load ho rahe hain...")
    data = await get_flipkart_trending()
    response = "\n\n---\n\n".join(data) if data else "Kuch nahi mila."
    await msg.edit_text(f"🔥 **Flipkart Top Trending:**\n\n{response}", disable_web_page_preview=True)

@Client.on_message(filters.command("meesho") & filters.private)
async def meesho_cmd(client, message):
    msg = await message.reply_text("🔎 Meesho ka data load kar raha hu...")
    data = await get_meesho_trending()
    response = "\n\n---\n\n".join(data) if data else "Kuch nahi mila."
    await msg.edit_text(f"🔥 **Meesho Top Trending:**\n\n{response}")
