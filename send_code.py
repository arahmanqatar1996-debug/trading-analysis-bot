#!/usr/bin/env python3
"""
Script to send code files directly to Telegram Bot via messages
"""

import requests

# User's credentials
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
    response = requests.post(url, data=data, timeout=30)
    return response.json()

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def main():
    print("Sending code to Telegram...")

    # Send intro
    send_message("📦 *Trading Bot - সম্পূর্ণ কোড*\n\n━━━━━━━━━━━━━━━━━")

    # Send main.py
    main_py = read_file("/workspace/trading-bot/main.py")
    chunks = [main_py[i:i+4000] for i in range(0, len(main_py), 4000)]
    send_message("🤖 *main.py* (1/" + str(len(chunks)) + ")")
    for i, chunk in enumerate(chunks):
        send_message("```python\n" + chunk + "\n```")
        print(f"Sent main.py part {i+1}/{len(chunks)}")

    send_message("✅ main.py সম্পূর্ণ পাঠানো হয়েছে!\n\n_পরবর্তী ফাইল আসছে..._")

    # Send config.py
    config_py = read_file("/workspace/trading-bot/config.py")
    send_message("⚙️ *config.py*\n\n```python\n" + config_py + "\n```")
    print("Sent config.py")

    # Send requirements.txt
    req = read_file("/workspace/trading-bot/requirements.txt")
    send_message("📋 *requirements.txt*\n\n```\n" + req + "\n```")
    print("Sent requirements.txt")

    # Send SETUP_GUIDE
    guide = read_file("/workspace/trading-bot/SETUP_GUIDE.md")
    guide_chunks = [guide[i:i+4000] for i in range(0, len(guide), 4000)]
    send_message("📝 *SETUP_GUIDE.md* - সেটআপ গাইড\n\n_এটি পড়ুন এবং ধাপে ধাপে follow করুন!_")
    for i, chunk in enumerate(guide_chunks):
        send_message(chunk)
        print(f"Sent guide part {i+1}/{len(guide_chunks)}")

    # Send final message
    send_message("✅ *সব কোড পাঠানো হয়েছে!*\n\nএখন:\n1. GitHub-এ repository বানান\n2. এই কোডগুলো upload করুন\n3. Render.com-এ deploy করুন\n\n_Questions? আমাকে জানান!_")

    print("\n🎉 সব কোড পাঠানো হয়েছে!")

if __name__ == "__main__":
    main()
