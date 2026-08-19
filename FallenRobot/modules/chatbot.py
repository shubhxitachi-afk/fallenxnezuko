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

    # Check if chatbot is enabled for this chat
    if not sql.is_fallen(chat.id):
        return

    if message.text.startswith(("/", "!", "#")):
        return

    # Trigger conditions
    is_reply_to_bot = (
        message.reply_to_message
        and message.reply_to_message.from_user.id == BOT_ID
    )
    is_tagged = BOT_USERNAME and f"@{BOT_USERNAME.lower()}" in message.text.lower()
    is_private = chat.type == "private"

    # If it's a group, reply if tagged or replied to bot
    if not (is_reply_to_bot or is_tagged or is_private):
        return

    user_text = message.text
    if BOT_USERNAME:
        user_text = user_text.replace(f"@{BOT_USERNAME}", "").replace(f"@{BOT_USERNAME.lower()}", "").strip()

    if not user_text:
        return

    context.bot.send_chat_action(chat.id, action="typing")

    # Ultra-Fast Free Chat Endpoint
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        api_url = f"https://api.simsimi.vn/v1/simtalk"
        payload = {"text": user_text, "lc": "hi"}  # Hindi / Hinglish mode
        res = requests.post(api_url, data=payload, headers=headers, timeout=6)
        if res.status_code == 200:
            reply = res.json().get("message")
            if reply and reply.strip():
                message.reply_text(reply)
                return
    except Exception:
        pass

    # Fallback 2: Pollinations AI
    try:
        url = f"https://text.pollinations.ai/{requests.utils.quote(user_text)}?model=openai"
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code == 200 and res.text.strip():
            message.reply_text(res.text.strip())
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
