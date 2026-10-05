def run_multi_agent_system():
    settings = load_user_settings()
    auto_limit = settings.get("auto_execution_limit", 150.0)
    rsi_low = settings.get("rsi_oversold", 35)
    rsi_high = settings.get("rsi_overbought", 70)
    
    logger.info(f"اعمال تنظیمات <- سقف RSI: {auto_limit} | خرید: {rsi_low} | فروش: {rsi_high}")
    
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
                    f"🚨 **معامله خودکار (Paper Trading)**\n\n"
                    f"🪙 **ارز:** `{symbol}`\n"
                    f"📈 **سیگنال:** `{signal_type}`\n"
                    f"💵 **قیمت:** `{current_price}` | RSI: `{rsi}`\n"
                    f"🛡️ **مبلغ تخصیص‌یافته:** `{proposed_amount}$` (زیر سقف انتخابی شما)"
                )
                send_telegram_msg(msg)
                logger.info(f"معامله خودکار برای {symbol} انجام شد.")
            else:
                keyboard = {
                    "inline_keyboard": [
                        [
                            {"text": "✅ تأیید و صدور مجوز", "callback_data": f"approve_{symbol}"},
                            {"text": "❌ رد کردن", "callback_data": f"reject_{symbol}"}
                        ]
                    ]
                }
                msg = (
                    f"⚠️ **درخواست تایید معامله (فراتر از سقف شما)**\n\n"
                    f"🪙 **ارز:** `{symbol}` | **سیگنال:** `{signal_type}`\n"
                    f"💵 **قیمت:** `{current_price}` | RSI: `{rsi}`\n"
                    f"🛡️ **مبلغ پیشنهادی:** `{proposed_amount}$`"
                )
                send_telegram_msg(msg, reply_markup=keyboard)
                logger.info(f"درخواست تایید برای {symbol} ارسال شد.")
        else:
            logger.info(f"در محدوده خنثی RSI شرایط ورود برای {symbol} نیست (RSI: {rsi}).")

    # ارسال گزارش سلامت (Heartbeat) در انتهای بررسی تمام ارزها (چه سیگنال باشد چه نباشد)
    heartbeat_msg = (
        "🤖 **گزارش سلامت سیستم (Heartbeat)**\n"
        f"📅 **زمان بررسی:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n"
        f"🛡️ **سقف بودجه خودکار شما:** `{auto_limit}$`\n"
        f"📊 **محدوده‌های RSI:** خرید < `{rsi_low}` | فروش > `{rsi_high}`\n"
        f"🔔 **سیگنال‌های این چرخه:** `{signals_found}`\n"
        f"🟢 **وضعیت ربات (Paper Trading):** فعال و پایدار"
    )
    send_telegram_msg(heartbeat_msg)
