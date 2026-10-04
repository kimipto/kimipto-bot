import json
import os

SETTINGS_FILE = "user_settings.json"

DEFAULT_SETTINGS = {
    "auto_execution_limit": 150.0,
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "paper_trading": True
}

def load_user_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_SETTINGS
    return DEFAULT_SETTINGS

def save_user_settings(settings):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        return False
