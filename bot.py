import os
import time
import requests
import json
import pandas as pd
import ccxt
from groq import Groq

# خواندن کلیدها از محیط امن گیت‌هاب
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

groq_client = Groq(api_key=GROQ_API_KEY)
exchange = ccxt.kucoin({'enableRateLimit': True})

def send_alert(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"Telegram Err: {e}")

def get_data(symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='15m', limit=50)
        df = pd.DataFrame(ohlcv, columns=['t', 'o', 'h', 'l', 'c', 'v'])
        delta = df['c'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        return True, df['c'].iloc[-1], round(rsi.iloc[-1], 2)
    except Exception as e:
        print(f"Data Err {symbol}: {e}")
        return False, None, None

def analyze(symbol, price, rsi):
    prompt = f"Analyze {symbol}: Price ${price}, RSI {rsi}. If RSI<35 BUY, if RSI>65 SELL, else HOLD. Return JSON: {{\"signal\": \"BUY|SELL|HOLD\", \"reasoning\": \"1 sentence\"}}"
    try:
        res = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})
        data = json.loads(res.choices[0].message.content)
        return data.get("signal", "HOLD"), data.get("reasoning", "")
    except:
        return ("BUY" if rsi < 35 else ("SELL" if rsi > 65 else "HOLD")), f"RSI: {rsi}"

def check_risk(symbol, price, rsi, signal, reasoning):
    if signal == "HOLD": return False, "HOLD Signal"
    prompt = f"Risk check {symbol}: Price ${price}, RSI {rsi}, Signal {signal}. Approve? Return JSON: {{\"approved\": true|false, \"risk_comment\": \"1 sentence\"}}"
    try:
        res = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})
        data = json.loads(res.choices[0].message.content)
        return data.get("approved", False), data.get("risk_comment", "")
    except:
        return True, "Approved (fallback)"

def run_cycle():
    print("\n--- Scanning Market ---")
    for s in SYMBOLS:
        ok, price, rsi = get_data(s)
        if not ok: continue
        sig, reason = analyze(s, price, rsi)
        app, risk = check_risk(s, price, rsi, sig, reason)
        print(f"[{s}] Price: ${price} | RSI: {rsi} | Signal: {sig} | Approved: {app}")
        if app:
            send_alert(f"🚨 *Kimipto Alert*\n\n🪙 `{s}`\n💵 `${price}`\n📊 RSI: `{rsi}`\n📈 Signal: `{sig}`\n🧠 {reason}\n🛡 {risk}")

if __name__ == "__main__":
    print("Kimipto AI Cloud Execution Started...")
    run_cycle()
