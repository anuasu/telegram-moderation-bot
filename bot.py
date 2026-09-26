import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import (
    setup_database,
    add_user,
    get_warnings,
    add_warning,
    remove_warning,
    reset_warnings,
    add_log
)

# =========================
# BOT CONFIG
# =========================

BOT_TOKEN = "8638240541:AAErXD7YUfMibgxs2ckfdygJeXW2CjV23SE"

ADMIN_IDS = [
    8115436142,
    7331380618
]

bot = telebot.TeleBot(BOT_TOKEN)

setup_database()

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
        bot.reply_to(
            message,
            "❌ You are not an admin."
        )
        return

    bot.reply_to(
        message,
        "👑 Admin Panel\n\n"
        "Bot is working correctly."
    )


# =========================
# WARNING SYSTEM
# =========================

MAX_WARNINGS = 3


def get_user_from_reply(message):

    if not message.reply_to_message:
        return None

    return message.reply_to_message.from_user


@bot.message_handler(commands=["warn"])
def warn_user(message):

    if not is_admin(message.from_user.id):
        bot.reply_to(
            message,
            "❌ Only admins can use this command."
        )
        return

    user = get_user_from_reply(message)

    if not user:
        bot.reply_to(
            message,
            "⚠️ Kisi user ke message ko reply karke /warn use karo."
        )
        return

    reason = message.text.replace("/warn", "", 1).strip()

    if not reason:
        reason = "No reason provided"

    # Save user
    add_user(
        user.id,
        user.username,
        user.first_name
    )

    # Add warning
    warnings = add_warning(user.id)

    admin_name = message.from_user.first_name

    # =========================
    # 3 WARNINGS = AUTO MUTE
    # =========================

    if warnings >= MAX_WARNINGS:

        try:

            bot.restrict_chat_member(
                message.chat.id,
                user.id,
                permissions=telebot.types.ChatPermissions(
                    can_send_messages=False
                )
            )

            action_text = "🔇 User has been muted automatically."

            add_log(
                user.id,
                message.from_user.id,
                "AUTO_MUTE",
                reason
            )

            # Reset warning count after mute
            reset_warnings(user.id)

        except Exception as e:

            action_text = (
                "⚠️ Auto mute failed.\n"
                f"Error: {e}"
            )

        text = (
            "⚠️ <b>WARNING ISSUED</b>\n\n"
            f"👤 User: {user.first_name}\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"⚠️ Warning: {MAX_WARNINGS}/{MAX_WARNINGS}\n"
            f"📝 Reason: {reason}\n"
            f"👮 By: {admin_name}\n\n"
            f"{action_text}"
        )

        bot.reply_to(
            message,
            text,
            parse_mode="HTML"
        )

    # =========================
    # NORMAL WARNING
    # =========================

    else:

        add_log(
            user.id,
            message.from_user.id,
            "WARN",
            reason
        )

        keyboard = InlineKeyboardMarkup()

        keyboard.add(
            InlineKeyboardButton(
                "🗑 Remove Warning",
                callback_data=f"remove_warn:{user.id}"
            )
        )

        text = (
            "⚠️ <b>WARNING ISSUED</b>\n\n"
            f"👤 User: {user.first_name}\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"⚠️ Warning: {warnings}/{MAX_WARNINGS}\n"
            f"📝 Reason: {reason}\n"
            f"👮 By: {admin_name}"
        )

        bot.reply_to(
            message,
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )


# =========================
# REMOVE ONE WARNING
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("remove_warn:")
)
def remove_warning_callback(call):

    if not is_admin(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "❌ Only admins can remove warnings.",
            show_alert=True
        )

        return

    user_id = int(
        call.data.split(":")[1]
    )

    current_warnings = get_warnings(user_id)

    if current_warnings <= 0:

        bot.answer_callback_query(
            call.id,
            "ℹ️ This user has no warnings.",
            show_alert=True
        )

        return

    new_count = remove_warning(user_id)

    add_log(
        user_id,
        call.from_user.id,
        "REMOVE_WARNING",
        "Warning removed by admin"
    )

    bot.answer_callback_query(
        call.id,
        f"✅ Warning removed. Now {new_count}/{MAX_WARNINGS}"
    )

    try:

        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )

    except Exception:
        pass

    bot.send_message(
        call.message.chat.id,
        "✅ <b>Warning Removed</b>\n\n"
        f"👤 User ID: <code>{user_id}</code>\n"
        f"⚠️ Current warnings: {new_count}/{MAX_WARNINGS}",
        parse_mode="HTML"
    )


# =========================
# TRACK USERS
# =========================

@bot.message_handler(func=lambda message: True)
def track_user(message):

    user = message.from_user

    add_user(
        user.id,
        user.username,
        user.first_name
    )


# =========================
# RUN BOT
# =========================

print("🤖 Bot started...")

bot.infinity_polling()