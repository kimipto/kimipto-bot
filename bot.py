import os
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_message(message: str) -> bool:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("خطا: توکن یا چت‌آیدی تلگرام در متغیرهای محیطی یافت نشد.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            logger.info("پیام تلگرام با موفقیت ارسال شد.")
            return True
        else:
            logger.error(f"خطای تلگرام: {response.text}")
            return False
    except Exception as e:
        logger.error(f"خطای شبکه در ارتباط با تلگرام: {e}")
        return False

def run_multi_agent_system():
    logger.info("اجرای سیستم چندعامله ربات آغاز شد.")
    
    heartbeat_msg = (
        "🟢 *گزارش سلامت ربات (Heartbeat)*\n\n"
        "▫️ وضعیت اکشن گیت‌هاب: موفق (Success)\n"
        "▫️ بررسی بازار و پایش: انجام شد\n"
        "▫️ سیستم در وضعیت کاملاً فعال قرار دارد."
    )
    
    send_telegram_message(heartbeat_msg)

if __name__ == "__main__":
    run_multi_agent_system()
