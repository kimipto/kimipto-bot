import time
import logging
import requests
import os
from datetime import datetime
from settings_manager import load_user_settings

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_TELEGRAM_CHAT_ID")

MAIN_ASSETS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
MEME_ASSETS = ["PEPEUSDT", "DOGEUSDT", "SHIBUSDT"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_telegram_message(text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        logger.error(f"خطا در ارسال پیام تلگرام: {e}")
        return None

def fetch_market_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=30m&limit=50"
        response = requests.get(url, timeout=10)
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            last_candle = data[-1]
            last_candle_time = datetime.fromtimestamp(last_candle[0] / 1000.0)
            logger.info(f"داده‌های {symbol} دریافت شد. زمان آخرین کندل: {last_candle_time}")
            closes = [float(candle[4]) for candle in data]
            return closes, last_candle_time
        return None, None
    except Exception as e:
        logger.error(f"خطا در دریافت داده برای {symbol}: {e}")
        return None, None

def calculate_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50.0
    gains, losses = 0.0, 0.0
    for i in range(1, period + 1):
        change = closes[-i] - closes[-i-1]
        if change > 0:
            gains += change
        else:
            losses -= change
    avg_gain = gains / period
    avg_loss = losses / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

def run_multi_agent_system():
    settings = load_user_settings()
    auto_limit = settings.get("auto_execution_limit", 150.0)
    rsi_low = settings.get("rsi_oversold", 30)
    rsi_high = settings.get("rsi_overbought", 70)
    
    logger.info(f"اعمال تنظیمات -> سقف خودکار: ${auto_limit} | RSI خرید: {rsi_low} | RSI فروش: {rsi_high}")
    
    all_assets = MAIN_ASSETS + MEME_ASSETS
    signals_found = 0
    
    for symbol in all_assets:
        closes, last_time = fetch_market_data(symbol)
        if not closes:
            continue
        
        current_price = closes[-1]
        rsi = calculate_rsi(closes)
        
        signal_type = None
        if rsi <= rsi_low:
            signal_type = "خرید (LONG)"
        elif rsi >= rsi_high:
            signal_type = "فروش (SHORT)"
            
        if signal_type:
            signals_found += 1
            proposed_amount = 100.0
            
            if proposed_amount <= auto_limit:
                msg = (
                    f"🤖 **معامله خودکار قائم‌مقام (Paper Trading)**\n"
                    f"▫️ ارز: `{symbol}`\n"
                    f"▫️ سیگنال: **{signal_type}**\n"
                    f"▫️️ قیمت: `{current_price}` | RSI: `{rsi}`\n"
                    f"▫️ مبلغ تخصیص‌یافته: `${proposed_amount}` (زیر سقف انتخابی شما: ${auto_limit})"
                )
                send_telegram_message(msg)
                logger.info(f"معامله خودکار برای {symbol} انجام شد.")
            else:
                keyboard = {
                    "inline_keyboard": [
                        [
                            {"text": "✅ تایید و صدور مجوز", "callback_data": f"approve_{symbol}"},
                            {"text": "❌ رد کردن", "callback_data": f"reject_{symbol}"}
                        ]
                    ]
                }
                msg = (
                    f"⚠️ **درخواست تایید معامله (فراتر از سقف شما: ${auto_limit})**\n"
                    f"▫️️ ارز: `{symbol}` | سیگنال: **{signal_type}**\n"
                    f"▫️ قیمت: `{current_price}` | RSI: `{rsi}`\n"
                    f"▫️️ مبلغ پیشنهادی: `${proposed_amount}`"
                )
                send_telegram_message(msg, reply_markup=keyboard)
        else:
            logger.info(f"شرایط ورود برای {symbol} برقرار نیست (RSI در محدوده خنثی: {rsi}).")

    heartbeat_msg = (
        f"💓 **گزارش سلامت سیستم (Heartbeat)**\n"
        f"▫️ زمان بررسی: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n"
        f"▫️ سقف بودجه خودکار شما: `${auto_limit}`\n"
        f"▫️ محدوده‌های RSI: خرید < `{rsi_low}` | فروش > `{rsi_high}`\n"
        f"▫️ سیگنال‌های این چرخه: `{signals_found}`\n"
        f"▫️ وضعیت ربات: `فعال و پایدار (Paper Trading)`"
    )
    send_telegram_message(heartbeat_msg)

if __name__ == "__main__":
    run_multi_agent_system()
