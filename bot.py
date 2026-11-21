
import os
import re
import socket
import requests
import phonenumbers

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

BOT_TOKEN = os.getenv("8741452115:AAFm8xLd24BPhRAc_re_GASKSnurIGjepQs")
GROQ_API_KEY = os.getenv("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")

WELCOME = """
⚡ OPTIMUS-X
━━━━━━━━━━━━━━━━━━
Your Smart AI & Public OSINT Assistant

Choose a service below:
"""

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Domain Lookup", callback_data="domain"),
         InlineKeyboardButton("📡 IP Lookup", callback_data="ip")],
        [InlineKeyboardButton("📧 Email Check", callback_data="email"),
         InlineKeyboardButton("📱 Phone Check", callback_data="phone")],
        [InlineKeyboardButton("🔗 URL Security", callback_data="url"),
         InlineKeyboardButton("👤 Username Format", callback_data="username")],
        [InlineKeyboardButton("📢 Public Channel", callback_data="channel")],
        [InlineKeyboardButton("🤖 AI Assistant", callback_data="ask")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(WELCOME, reply_markup=menu())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Use the menu or commands:\n"
        "/domain example.com\n/ip 8.8.8.8\n"
        "/email test@example.com\n/phone +919876543210\n"
        "/url https://example.com\n/username example_user\n"
        "/channel public_channel"
    )

async def domain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /domain example.com")
    host = context.args[0].strip().lower()
    if not re.fullmatch(r"[a-z0-9.-]+\.[a-z]{2,}", host):
        return await update.message.reply_text("Invalid domain format.")
    try:
        ip = socket.gethostbyname(host)
        await update.message.reply_text(f"🌐 Domain: {host}\n📡 IPv4: {ip}")
    except Exception:
        await update.message.reply_text("Domain could not be resolved.")

async def ip_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /ip 8.8.8.8")
    ip = context.args[0]
    try:
        import ipaddress
        address = ipaddress.ip_address(ip)
        if not address.is_global:
            return await update.message.reply_text("Only public IP information is supported.")
        data = requests.get(
            f"http://ip-api.com/json/{ip}",
            params={"fields": "status,country,regionName,city,isp,query"},
            timeout=8
        ).json()
        if data.get("status") != "success":
            raise ValueError()
        await update.message.reply_text(
            f"📡 IP: {data['query']}\n"
            f"🌍 Country: {data.get('country')}\n"
            f"📍 Region: {data.get('regionName')}\n"
            f"🏙 City: {data.get('city')}\n"
            f"🏢 ISP: {data.get('isp')}\n\n"
            "Approximate network information only."
        )
    except Exception:
        await update.message.reply_text("Invalid IP or lookup unavailable.")

async def email_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /email test@example.com")
    email = context.args[0].strip()
    valid = bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))
    await update.message.reply_text(
        "✅ Email syntax looks valid." if valid
        else "❌ Invalid email syntax."
    )

async def phone_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /phone +919876543210")
    try:
        number = phonenumbers.parse(context.args[0], None)
        valid = phonenumbers.is_valid_number(number)
        country = phonenumbers.region_code_for_number(number)
        await update.message.reply_text(
            f"📱 Valid format: {valid}\n🌍 Country code region: {country}\n"
            "No subscriber identity or live location is provided."
        )
    except Exception:
        await update.message.reply_text("Please enter a number with country code.")

async def url_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /url https://example.com")
    url = context.args[0].strip()
    if not re.match(r"^https?://", url, re.I):
        return await update.message.reply_text("Enter a URL starting with http:// or https://")
    suspicious = (
        len(url) > 200 or "@" in url.split("://", 1)[-1]
        or url.lower().startswith("http://")
    )
    await update.message.reply_text(
        f"🔗 URL: {url}\n"
        f"⚠️ Basic heuristic: {'Potentially suspicious' if suspicious else 'No basic warning detected'}\n"
        "This is not a guarantee that the site is safe."
    )

async def username_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /username example_user")
    name = context.args[0].lstrip("@")
    valid = bool(re.fullmatch(r"[A-Za-z0-9_]{5,32}", name))
    await update.message.reply_text(
        "✅ Username format looks valid." if valid
        else "❌ Username format is invalid."
    )

async def channel_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /channel public_channel")
    channel = context.args[0]
    if not channel.startswith("@"):
        channel = "@" + channel
    try:
        chat = await context.bot.get_chat(channel)
        await update.message.reply_text(
            f"📢 Public channel information\n"
            f"Name: {chat.title}\n"
            f"Username: {chat.username}\n"
            f"Type: {chat.type}\n"
            f"Description: {chat.description or 'Not available'}"
        )
    except Exception:
        await update.message.reply_text("Public channel information unavailable.")

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not GROQ_API_KEY:
        return await update.message.reply_text("AI is not configured. Add GROQ_API_KEY.")
    if not context.args:
        return await update.message.reply_text("Usage: /ask your question")
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        result = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "You are Optimus-X. Answer helpfully: " + " ".join(context.args)}],
            max_tokens=500
        )
        await update.message.reply_text(result.choices[0].message.content)
    except Exception:
        await update.message.reply_text("AI service is temporarily unavailable.")

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    actions = {
        "domain": ("🌐 Send domain using /domain example.com", "domain"),
        "ip": ("📡 Send public IP using /ip 8.8.8.8", "ip"),
        "email": ("📧 Send email using /email test@example.com", "email"),
        "phone": ("📱 Send phone using /phone +919876543210", "phone"),
        "url": ("🔗 Send URL using /url https://example.com", "url"),
        "username": ("👤 Send a username using /username example_user", "username"),
        "channel": ("📢 Send public channel using /channel @channel", "channel"),
        "ask": ("🤖 Ask AI using /ask your question", "ask")
    }
    message, _ = actions.get(query.data, ("Unknown option", ""))
    await query.message.reply_text(message)

async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is missing.")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("domain", domain))
    app.add_handler(CommandHandler("ip", ip_lookup))
    app.add_handler(CommandHandler("email", email_check))
    app.add_handler(CommandHandler("phone", phone_check))
    app.add_handler(CommandHandler("url", url_check))
    app.add_handler(CommandHandler("username", username_check))
    app.add_handler(CommandHandler("channel", channel_info))
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(CallbackQueryHandler(buttons))
    print("Optimus-X is running...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    import asyncio
    await asyncio.Event().wait()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
