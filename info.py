import os

# os.environ.get() ka matlab hai pehle server ke secrets me check karo, 
# agar waha nahi hai to default value (jo comma ke baad hai) use karo.

API_ID = int(os.environ.get("API_ID", 12345678))  # Apna API ID yahan dalein (Ye number hona chahiye)
API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH") # Apna API HASH yahan dalein
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN") # Apna BOT TOKEN yahan dalein

# Agar aapko future mein MongoDB ya Owner ID add karni ho, to yahan kar sakte hain
# MONGO_URI = os.environ.get("MONGO_URI", "YOUR_MONGO_URL")
# OWNER_ID = int(os.environ.get("OWNER_ID", 123456789))
