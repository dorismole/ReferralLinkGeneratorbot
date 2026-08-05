import os
import urllib.parse
import telebot
from telebot import types

# Get Bot Token from Railway Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is missing!")

bot = telebot.TeleBot(BOT_TOKEN)

# Memory storage for temporary user inputs
user_data = {}


def get_keyboard():
    """Create interactive mode keyboard."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_custom = types.InlineKeyboardButton("🔗 Custom Parameter Link", callback_data="mode_custom")
    btn_utm = types.InlineKeyboardButton("📊 UTM Tracked Link", callback_data="mode_utm")
    btn_telegram = types.InlineKeyboardButton("✈️ Telegram Bot Deep Link", callback_data="mode_tg")
    
    markup.add(btn_custom, btn_utm, btn_telegram)
    return markup


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    welcome_text = (
        "<b>🔗 Referral Link Generator Bot</b>\n\n"
        "Generate clean, tracked referral links and invite parameters instantly!\n\n"
        "<b>Quick Usage:</b>\n"
        "Send your base link and referral code in this format:\n"
        "<code>https://example.com | mycode123</code>\n\n"
        "Or pick a generator mode below:"
    )

    bot.send_message(
        chat_id=message.chat.id,
        text=welcome_text,
        parse_mode="HTML",
        reply_markup=get_keyboard()
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("mode_"))
def handle_mode_click(call):
    mode = call.data.replace("mode_", "")
    
    instructions = {
        "custom": "Send your URL and code separated by <code>|</code>:\n\n<i>Example:</i> <code>https://myapp.com | USER99</code>",
        "utm": "Send your URL, campaign name, and ref code:\n\n<i>Example:</i> <code>https://myapp.com | summer_sale | USER99</code>",
        "tg": "Send your Telegram bot username and ref code:\n\n<i>Example:</i> <code>MyCoolBot | REF12345</code>"
    }
    
    text = f"<b>⚙️ Mode Selected</b>\n\n{instructions.get(mode, '')}"
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text, parse_mode="HTML")


@bot.message_handler(func=lambda message: True)
def process_link_request(message):
    raw_text = message.text.strip()
    parts = [p.strip() for p in raw_text.split("|")]

    if len(parts) < 2:
        error_msg = (
            "⚠️ <b>Invalid Format!</b>\n\n"
            "Please separate parameters using the pipe character (<code>|</code>).\n\n"
            "<b>Example:</b>\n"
            "<code>https://example.com | REF123</code>"
        )
        bot.reply_to(message, error_msg, parse_mode="HTML")
        return

    base_url = parts[0]
    ref_code = parts[1]

    # Clean base URL formatting
    if not base_url.startswith("http://") and not base_url.startswith("https://") and not base_url.endswith("bot"):
        base_url = "https://" + base_url

    # Check for Telegram bot deep link format
    if "t.me/" in base_url or base_url.lower().endswith("bot"):
        bot_username = base_url.replace("https://t.me/", "").replace("http://t.me/", "").replace("@", "")
        clean_code = "".join(e for e in ref_code if e.isalnum() or e == "_")
        
        link1 = f"https://t.me/{bot_username}?start={clean_code}"
        link2 = f"https://t.me/{bot_username}?startapp={clean_code}"

        response = (
            "<b>✈️ Telegram Deep Referral Links Generated:</b>\n\n"
            f"<b>Standard Bot Link:</b>\n<code>{link1}</code>\n\n"
            f"<b>Mini App Link:</b>\n<code>{link2}</code>\n\n"
            "👇 <i>Tap any link box above to copy automatically!</i>"
        )
    else:
        # Web Referral variations
        encoded_code = urllib.parse.quote(ref_code)
        
        # Build variations
        param_char = "&" if "?" in base_url else "?"
        
        ref_link = f"{base_url}{param_char}ref={encoded_code}"
        invite_link = f"{base_url}{param_char}invite={encoded_code}"
        code_link = f"{base_url}{param_char}code={encoded_code}"
        
        utm_campaign = parts[2] if len(parts) > 2 else "referral"
        utm_link = f"{base_url}{param_char}utm_source=referral&utm_campaign={urllib.parse.quote(utm_campaign)}&ref={encoded_code}"

        response = (
            f"<b>🔗 Referral Links Generated for:</b> <code>{ref_code}</code>\n\n"
            f"<b>1. Standard Ref Param (?ref=):</b>\n<code>{ref_link}</code>\n\n"
            f"<b>2. Invite Param (?invite=):</b>\n<code>{invite_link}</code>\n\n"
            f"<b>3. Code Param (?code=):</b>\n<code>{code_link}</code>\n\n"
            f"<b>4. Tracked UTM Link:</b>\n<code>{utm_link}</code>\n\n"
            "👇 <i>Tap any link box above to copy automatically!</i>"
        )

    bot.send_message(
        chat_id=message.chat.id,
        text=response,
        parse_mode="HTML",
        reply_markup=get_keyboard()
    )


if __name__ == "__main__":
    print("Referral Link Generator Bot is running...")
    bot.infinity_polling()
