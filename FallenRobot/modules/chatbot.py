import html
import json
import re
from time import sleep
import requests
from telegram import (
    CallbackQuery,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
    User,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    run_async,
)
from telegram.utils.helpers import mention_html

import FallenRobot.modules.sql.chatbot_sql as sql
from FallenRobot import BOT_ID, BOT_NAME, BOT_USERNAME, dispatcher
from FallenRobot.modules.helper_funcs.chat_status import user_admin, user_admin_no_reply
from FallenRobot.modules.log_channel import gloggable


@run_async
@user_admin_no_reply
@gloggable
def chatbot(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    message = update.effective_message
    msg = "Choose an option"
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
                f"Chatbot is already enabled in <b>{chat.title}</b>.",
                parse_mode=ParseMode.HTML,
            )
        else:
            sql.set_fallen(chat.id)
            query.answer("Chatbot enabled successfully.")
            query.message.edit_text(
                f"Chatbot enabled by {query.from_user.first_name} for <b>{chat.title}</b>.",
                parse_mode=ParseMode.HTML,
            )
    elif switcher == "rm_chat":
        is_fallen = sql.is_fallen(chat.id)
        if not is_fallen:
            query.answer("Chatbot is already disabled.")
            query.message.edit_text(
                f"Chatbot is already disabled in <b>{chat.title}</b>.",
                parse_mode=ParseMode.HTML,
            )
        else:
            sql.rem_fallen(chat.id)
            query.answer("Chatbot disabled successfully.")
            query.message.edit_text(
                f"Chatbot disabled by {query.from_user.first_name} for <b>{chat.title}</b>.",
                parse_mode=ParseMode.HTML,
            )


@run_async
def fallen_message(update: Update, context: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if message.text and not message.document:
        if not sql.is_fallen(chat.id):
            return

        if message.text.startswith(("/", "!", "#")):
            return

        if message.reply_to_message:
            if message.reply_to_message.from_user.id != BOT_ID:
                return

        context.bot.send_chat_action(chat.id, action="typing")
        user_input = message.text

        # Working Fast Free AI Endpoint
        url = f"https://api.affiliateplus.xyz/api/chatbot?message={requests.utils.quote(user_input)}&botname={BOT_NAME}&ownername=Shubh&user={user.id}"
        
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                bot_reply = res.json().get("message")
                if bot_reply:
                    message.reply_text(bot_reply)
                    return
        except Exception:
            pass

        # Fallback Backup API
        try:
            fallback_url = f"https://kuki-api.vercel.app/api/apikey=Kuki-0192837465/message={requests.utils.quote(user_input)}"
            res = requests.get(fallback_url, timeout=5)
            if res.status_code == 200:
                bot_reply = res.json().get("reply")
                if bot_reply:
                    message.reply_text(bot_reply)
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
