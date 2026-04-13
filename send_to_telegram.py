#!/usr/bin/env python3
"""
Script to send code files directly to Telegram Bot
"""

import requests
import os

TELEGRAM_BOT_TOKEN = "8269257402:AAEb2RMKL3r2CJQC10H4YBRhFI-rx-PhVhg"
TELEGRAM_CHAT_ID = "-1002986335453"
API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send_message(text):
    """Send message to Telegram"""
    url = f"{API_URL}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=data)
    return response.json()

def send_document(file_path, caption=""):
    """Send document to Telegram"""
    url = f"{API_URL}/sendDocument"
    with open(file_path, 'rb') as f:
        files = {'document': f}
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'caption': caption
        }
        response = requests.post(url, data=data, files=files)
    return response.json()

def main():
    print("Sending code files to Telegram...")

    # Send intro message
    send_message("📦 *Trading Bot Code Files*\n\nআপনার জন্য সম্পূর্ণ কোড পাঠাচ্ছি!")

    # Send files
    files_to_send = [
        ("/workspace/trading-bot/main.py", "🤖 main.py - Bot এর মূল কোড"),
        ("/workspace/trading-bot/config.py", "⚙️ config.py - কনফিগারেশন"),
        ("/workspace/trading-bot/market_data.py", "📊 market_data.py - মার্কেট ডাটা"),
        ("/workspace/trading-bot/strategies.py", "📈 strategies.py - ট্রেডিং স্ট্র্যাটেজি"),
        ("/workspace/trading-bot/requirements.txt", "📋 requirements.txt - প্যাকেজ লিস্ট"),
    ]

    for file_path, caption in files_to_send:
        if os.path.exists(file_path):
            print(f"Sending {file_path}...")
            result = send_document(file_path, caption)
            if result.get('ok'):
                print(f"✅ Sent {file_path}")
            else:
                print(f"❌ Failed to send {file_path}: {result}")
        else:
            print(f"⚠️ File not found: {file_path}")

    # Send setup guide
    if os.path.exists("/workspace/trading-bot/SETUP_GUIDE.md"):
        print("Sending SETUP_GUIDE.md...")
        result = send_document("/workspace/trading-bot/SETUP_GUIDE.md", "📝 SETUP_GUIDE.md - সেটআপ গাইড")
        if result.get('ok'):
            print("✅ Sent SETUP_GUIDE.md")
        else:
            print(f"❌ Failed to send SETUP_GUIDE.md: {result}")

    # Send final message
    send_message("✅ *সব কোড পাঠানো হয়েছে!*\n\nএখন GitHub/Render.com-এ deploy করুন।\n\nSetup Guide পড়ুন এবং ধাপে ধাপে follow করুন।")

    print("\n🎉 সব কোড Telegram-এ পাঠানো হয়েছে!")

if __name__ == "__main__":
    main()
