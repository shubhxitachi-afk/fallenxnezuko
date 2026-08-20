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

from FallenRobot import BOT_ID, BOT_NAME, BOT_USERNAME, dispatcher
from FallenRobot.modules.helper_funcs.chat_status import user_admin_no_reply
from FallenRobot.modules.log_channel import gloggable
import FallenRobot.modules.sql.chatbot_sql as sql

LOGGER = logging.getLogger(__name__)


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
        sql.set_fallen(chat.id)
        query.answer("Chatbot enabled successfully.")
        query.message.edit_text(
            f"Chatbot enabled by {query.from_user.first_name} for <b>{html.escape(chat.title)}</b>.",
            parse_mode=ParseMode.HTML,
        )
    elif switcher == "rm_chat":
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

    if not message:
        return

    # Check if replied to bot, tagged, or in private DM
    is_reply_to_bot = (
        message.reply_to_message
        and message.reply_to_message.from_user
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

    # Message text preparation
    if message.text:
        user_text = message.text
        if BOT_USERNAME:
            user_text = (
                user_text.replace(f"@{BOT_USERNAME}", "")
                .replace(f"@{BOT_USERNAME.lower()}", "")
                .strip()
            )
        prompt = user_text
    elif message.sticker:
        emoji = message.sticker.emoji or "sticker"
        prompt = f"User sent sticker: {emoji}. React/roast in savage Hinglish."
    else:
        return

    if not prompt:
        return

    context.bot.send_chat_action(chat.id, action="typing")

    system_instruction = (
        f"You are {BOT_NAME}, an Indian Telegram AI bot. "
        "Talk naturally in witty, savage Hinglish (Hindi + English). "
        "Keep replies crisp (1-2 sentences)."
    )

    try:
        query_text = f"{system_instruction}\nUser: {prompt}\n{BOT_NAME}:"
        encoded_query = requests.utils.quote(query_text)
        url = f"https://text.pollinations.ai/{encoded_query}"
        
        res = requests.get(url, timeout=10)
        if res.status_code == 200 and res.text.strip():
            message.reply_text(res.text.strip())
            return
        else:
            LOGGER.error(f"[Chatbot] API Response Error: {res.status_code}")
    except Exception as e:
        LOGGER.error(f"[Chatbot] Request Exception: {e}")


CHATBOT_HANDLER = CommandHandler("chatbot", chatbot, filters=Filters.chat_type.groups)
ADD_CHAT_HANDLER = CallbackQueryHandler(chatbot_status, pattern=r"add_chat")
RM_CHAT_HANDLER = CallbackQueryHandler(chatbot_status, pattern=r"rm_chat")

CHATBOT_MSG_HANDLER = MessageHandler(
    (Filters.text | Filters.sticker) & (~Filters.command),
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
