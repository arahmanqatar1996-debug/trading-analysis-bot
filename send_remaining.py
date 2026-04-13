#!/usr/bin/env python3
"""
Script to send remaining code files to Telegram
"""

import requests

TELEGRAM_BOT_TOKEN = "8269257402:AAEb2RMKL3r2CJQC10H4YBRhFI-rx-PhVhg"
TELEGRAM_CHAT_ID = "-1002986335453"
API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send_message(text):
    url = f"{API_URL}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=data, timeout=30)
    return response.json()

def main():
    print("Sending remaining files to Telegram...")

    # Send intro
    send_message("📦 *বাকি কোড ফাইলসমূহ*\n\n━━━━━━━━━━━━━━━━━")

    # Send market_data.py
    with open("/workspace/trading-bot/market_data.py", 'r') as f:
        market_data_py = f.read()

    chunks = [market_data_py[i:i+4000] for i in range(0, len(market_data_py), 4000)]
    send_message("📊 *market_data.py* (1/" + str(len(chunks)) + ")")
    for i, chunk in enumerate(chunks):
        send_message("```python\n" + chunk + "\n```")
        print(f"Sent market_data.py part {i+1}/{len(chunks)}")

    send_message("✅ market_data.py সম্পূর্ণ!\n\n_পরবর্তী ফাইল আসছে..._")

    # Send strategies.py
    with open("/workspace/trading-bot/strategies.py", 'r') as f:
        strategies_py = f.read()

    chunks = [strategies_py[i:i+4000] for i in range(0, len(strategies_py), 4000)]
    send_message("📈 *strategies.py* - ট্রেডিং স্ট্র্যাটেজি (1/" + str(len(chunks)) + ")")
    for i, chunk in enumerate(chunks):
        send_message("```python\n" + chunk + "\n```")
        print(f"Sent strategies.py part {i+1}/{len(chunks)}")

    send_message("✅ strategies.py সম্পূর্ণ!\n\n_সব কোড পাঠানো হয়েছে!_")

    # Send final message
    send_message("🎉 *সম্পূর্ণ কোড পাঠানো হয়েছে!*\n\nএখন সব ফাইল পেয়েছেন:\n"
                 "✅ main.py\n"
                 "✅ config.py\n"
                 "✅ market_data.py\n"
                 "✅ strategies.py\n"
                 "✅ requirements.txt\n"
                 "✅ SETUP_GUIDE.md\n\n"
                 "এখন GitHub/Render.com-এ deploy করুন!")

    print("\n🎉 সব ফাইল পাঠানো হয়েছে!")

if __name__ == "__main__":
    main()
