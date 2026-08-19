import html
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

# Free Google Gemini API Key
GEMINI_API_KEY = "AQ.Ab8RN6Jc8Xc1SXFL3RaVf-rCwBqnxFBgKQ1DfbS2IXUAYc7UOA"


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

    if not message.text or message.document:
        return

    if not sql.is_fallen(chat.id):
        return

    if message.text.startswith(("/", "!", "#")):
        return

    is_reply_to_bot = (
        message.reply_to_message
        and message.reply_to_message.from_user.id == BOT_ID
    )
    is_tagged = BOT_USERNAME and f"@{BOT_USERNAME.lower()}" in message.text.lower()
    is_private = chat.type == "private"

    if not (is_reply_to_bot or is_tagged or is_private):
        return

    user_text = message.text
    if BOT_USERNAME:
        user_text = user_text.replace(f"@{BOT_USERNAME}", "").replace(f"@{BOT_USERNAME.lower()}", "").strip()

    if not user_text:
        return

    context.bot.send_chat_action(chat.id, action="typing")

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                f"You are {BOT_NAME}, an Indian Telegram AI bot with a savage, witty, and friendly personality. "
                                "Reply naturally in Hindi/Hinglish (mix of Hindi & English). "
                                "If the user asks to roast or jokes with you, give funny, sharp, savage roasts in pure Hinglish slang. Keep responses crisp (1-3 sentences).\n\n"
                                f"User: {user_text}"
                            )
                        }
                    ]
                }
            ]
        }
        res = requests.post(url, json=payload, timeout=8)
        if res.status_code == 200:
            data = res.json()
            reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
            if reply_text:
                message.reply_text(reply_text.strip())
                return
    except Exception:
        pass


CHATBOT_HANDLER = CommandHandler("chatbot", chatbot, filters=Filters.chat_type.groups)
ADD_CHAT_HANDLER = CallbackQueryHandler(chatbot_status, pattern=r"add_chat")
RM_CHAT_HANDLER = CallbackQueryHandler(chatbot_status, pattern=r"rm_chat")
CHATBOT_MSG_HANDLER = MessageHandler(
    Filters.text & (~Filters.regex(r"^/")),
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
