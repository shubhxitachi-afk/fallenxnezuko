import html
import logging
import requests
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    run_async,
)

import FallenRobot.modules.sql.chatbot_sql as sql
from FallenRobot import BOT_ID, BOT_NAME, BOT_USERNAME, dispatcher
from FallenRobot.modules.helper_funcs.chat_status import user_admin_no_reply
from FallenRobot.modules.log_channel import gloggable

LOGGER = logging.getLogger(__name__)

# Google Gemini API Key
GEMINI_API_KEY = "AQ.Ab8RN6Kqz-DaYYXnS5DdSWqjospw_icTo-_yXjlC88_db_hETg"


@run_async
@user_admin_no_reply
@gloggable
def chatbot(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    msg = "Choose an option to enable or disable Chatbot:"
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="Enable", callback_data="add_chat"),
                InlineKeyboardButton(text="Disable", callback_data="rm_chat"),
            ]
        ]
    )
    message.reply_text(
        text=msg,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )


@run_async
def chatbot_status(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = update.effective_chat
    switcher = query.data
    if switcher == "add_chat":
        is_fallen = sql.is_fallen(chat.id)
        if is_fallen:
            query.answer("Chatbot is already enabled.")
            query.message.edit_text(
                f"Chatbot is already enabled in <b>{html.escape(chat.title)}</b>.",
                parse_mode=ParseMode.HTML,
            )
        else:
            sql.set_fallen(chat.id)
            query.answer("Chatbot enabled successfully.")
            query.message.edit_text(
                f"Chatbot enabled by {query.from_user.first_name} for <b>{html.escape(chat.title)}</b>.",
                parse_mode=ParseMode.HTML,
            )
    elif switcher == "rm_chat":
        is_fallen = sql.is_fallen(chat.id)
        if not is_fallen:
            query.answer("Chatbot is already disabled.")
            query.message.edit_text(
                f"Chatbot is already disabled in <b>{html.escape(chat.title)}</b>.",
                parse_mode=ParseMode.HTML,
            )
        else:
            sql.rem_fallen(chat.id)
            query.answer("Chatbot disabled successfully.")
            query.message.edit_text(
                f"Chatbot disabled by {query.from_user.first_name} for <b>{html.escape(chat.title)}</b>.",
                parse_mode=ParseMode.HTML,
            )


@run_async
def fallen_message(update: Update, context: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat

    if not sql.is_fallen(chat.id):
        return

    if message.text and message.text.startswith(("/", "!", "#")):
        return

    is_reply_to_bot = (
        message.reply_to_message
        and message.reply_to_message.from_user.id == BOT_ID
    )
    is_tagged = bool(
        message.text
        and BOT_USERNAME
        and f"@{BOT_USERNAME.lower()}" in message.text.lower()
    )
    is_private = chat.type == "private"

    if not (is_reply_to_bot or is_tagged or is_private):
        return

    if message.text:
        user_text = message.text
        if BOT_USERNAME:
            user_text = (
                user_text.replace(f"@{BOT_USERNAME}", "")
                .replace(f"@{BOT_USERNAME.lower()}", "")
                .strip()
            )
        prompt_content = f"User says: {user_text}"
    elif message.sticker:
        sticker_emoji = message.sticker.emoji or "random sticker"
        prompt_content = f"User sent this sticker emoji: {sticker_emoji}. Give a short funny or roast reply in Hinglish."
    else:
        return

    if not prompt_content.strip():
        return

    context.bot.send_chat_action(chat.id, action="typing")

    system_instruction = (
        f"You are {BOT_NAME}, a savage, witty Indian Telegram chatbot. "
        "Reply in Hinglish (Hindi + English). If the user asks for roast or sends stickers, "
        "give a funny and savage comeback. Keep it short (1-2 lines)."
    )

    # 1. Try Gemini API
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_instruction}\n\n{prompt_content}"}
                    ]
                }
            ]
        }
        res = requests.post(url, json=payload, timeout=7)
        if res.status_code == 200:
            reply_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            if reply_text:
                message.reply_text(reply_text.strip())
                return
        else:
            LOGGER.error(f"[Chatbot] Gemini Error: {res.status_code} - {res.text}")
    except Exception as e:
        LOGGER.error(f"[Chatbot] Gemini Exception: {e}")

    # 2. Automatic Backup AI (Pollinations)
    try:
        fallback_prompt = requests.utils.quote(f"{system_instruction}\n{prompt_content}")
        url_fallback = f"https://text.pollinations.ai/{fallback_prompt}"
        res_fb = requests.get(url_fallback, timeout=8)
        if res_fb.status_code == 200 and res_fb.text.strip():
            message.reply_text(res_fb.text.strip())
            return
    except Exception as e:
        LOGGER.error(f"[Chatbot] Fallback Error: {e}")


CHATBOT_HANDLER = CommandHandler("chatbot", chatbot, filters=Filters.chat_type.groups)
ADD_CHAT_HANDLER = CallbackQueryHandler(chatbot_status, pattern=r"add_chat")
RM_CHAT_HANDLER = CallbackQueryHandler(chatbot_status, pattern=r"rm_chat")

CHATBOT_MSG_HANDLER = MessageHandler(
    (Filters.text | Filters.sticker) & (~Filters.regex(r"^/")),
    fallen_message,
)

dispatcher.add_handler(CHATBOT_HANDLER)
dispatcher.add_handler(ADD_CHAT_HANDLER)
dispatcher.add_handler(RM_CHAT_HANDLER)
dispatcher.add_handler(CHATBOT_MSG_HANDLER)

__mod_name__ = "Chatbot"
__help__ = """
*Chatbot Module*

Commands:
 • /chatbot: Enables or disables chatbot in the chat.
"""
