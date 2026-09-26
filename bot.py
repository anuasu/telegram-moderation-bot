import telebot

# =========================
# BOT CONFIG
# =========================

BOT_TOKEN = "8638240541:AAErXD7YUfMibgxs2ckfdygJeXW2CjV23SE"

ADMIN_IDS = [
    8115436142,
    7331380618
]

bot = telebot.TeleBot(BOT_TOKEN)


# =========================
# HELPERS
# =========================

def is_admin(user_id):
    return user_id in ADMIN_IDS


# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "👋 Welcome!\n\n"
        "Moderation Bot is online."
    )


# =========================
# ADMIN TEST
# =========================

@bot.message_handler(commands=["admin"])
def admin(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ You are not an admin.")
        return

    bot.reply_to(
        message,
        "👑 Admin Panel\n\n"
        "Bot is working correctly."
    )


# =========================
# RUN BOT
# =========================

print("🤖 Bot started...")

bot.infinity_polling()
