import os
import telebot

from meta_ddb import get_user_meta_add_if_none, extract_categories
from utils import split_3_parts
from accounting import expense_handler
from handlers import category, guided_input, report, export
# Bot token from environment variable
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded = False)

category.register_category_handlers(bot)
guided_input.register_guided_input_handlers(bot)
report.register_report_handlers(bot)
export.register_export_handlers(bot)

@bot.message_handler(commands=['category'])
def category_command(message):
    user_meta = get_user_meta_add_if_none(message.from_user.username)
    expense_categories = extract_categories(user_meta)
    bot.send_message(message.chat.id, f"Valid category are {expense_categories}")

@bot.message_handler(commands=["help"])
def help_command(message):
  bot.reply_to(message,
               """
**Direct-to-action accounting commands** take the form:  
`<value> <category> <optional notes>`

For example:  
`9.45 food mc spicy`

Alternatively, use `*/input*` for an interactive way to add entries.

Use `/category` to see all valid accounting categories, `/add_category` 
and `/remove_category` to manage custom expense categories.

- Use  `/undo` rectify erroneous entries
          """,
      parse_mode="Markdown"
    )
  
@bot.message_handler(commands=["undo"])
def undo_command(message):
  bot.reply_to(message,"""No undo function implemented, bot was designed as an append only ledger. 
              Use "credit" category to offset erroneous entries. eg. -20 credit fat fingers.""")
    

@bot.message_handler(func=lambda message: True)
def direct_action_handler(message):
    user = message.from_user.username
    text = message.text
    value, command, note = split_3_parts(text)
    user_meta = get_user_meta_add_if_none(message.from_user.username)
    expense_categories = extract_categories(user_meta)
    if command in expense_categories:
        expense_handler(bot, user, value, command, note, message)
    else:
        bot.send_message(message.chat.id, "Invalid command, not smart enough to understand that")

def lambda_handler(event, context):
    """
    Lambda function handler for processing Telegram bot webhook updates.
    """
    try:
        # Parse the incoming request from Telegram
        if event["httpMethod"] == "POST":
            request_body = event["body"]
            update = telebot.types.Update.de_json(request_body)
            # Process the update
            bot.process_new_updates([update])
            return {
                "statusCode": 200,
                "body": "Webhook processed successfully."
            }
        else:
            return {
                "statusCode": 405,
                "body": "Method Not Allowed"
            }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": f"Internal Server Error: {str(e)}"
        }