import os
import telebot

from ledger_ddb import get_record_from_ledger
from meta_ddb import get_user_meta_add_if_none, extract_categories
from utils import split_3_parts, generate_doc
from accounting import credit_handler, expense_handler
from handlers import category, guided_input
# Bot token from environment variable
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded = False)

category.register_category_handlers(bot)
guided_input.register_guided_input_handlers(bot)

    
@bot.message_handler(commands=['report'])
def report_handler(message):
    expenses = get_expenses(message.from_user.username, current_year_month)
    aggregated = {}
    total_spend = 0
    total_credit = 0
    
    for expense in expenses:
        category = expense['category']
        value = float(expense['value'])
        
        if category == 'credit':
          total_credit += value
          continue
        
        total_spend += value
        if category in aggregated:
            aggregated[category] += value
        else:
            aggregated[category] = value

    report = f"💰 *Expense Breakdown:*\n"
    for category, value in aggregated.items():
        emoji = category_emojis.get(category, "🎮")
        percentage = (value / total_spend) * 100
        report += f"  - {emoji} *{category.capitalize()}*: ${value:.2f} ({percentage:.2f}%)\n"
    
    report += f"\n*Total Expense*: ${total_spend:.2f}"
    report += f"\n*Total Credit*: ${total_credit:.2f}"
    report += f"\n📊 *Nett spending*: ${(total_spend+total_credit):.2f}\n\n"
    bot.send_message(message.chat.id, report, parse_mode="Markdown")

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

Use `/category` to see all valid accounting categories.  

- Use `/add_category <category>` to add a new category.  
  For example: `/add_category groceries`

- Use `/remove_category <category>` to remove an existing category.  
  For example: `/remove_category food`
              """,
      parse_mode="Markdown"
    )

@bot.message_handler(commands=['export'])
def export_command(message):
    expenses = get_expenses(message.from_user.username, current_year_month)
    if len(expenses) == 0:
        bot.send_message(message.chat.id, "you didnt spend shit this month")
    else:
        data = [["category", "value", "notes"]] # Add headers
        data += [[expense['category'], expense['value'], expense['notes']] for expense in expenses]
        bot.send_document(message.chat.id, document=generate_doc(data))

def get_expenses(username, year_month):
    response = get_record_from_ledger(username, year_month)
    if 'Item' in response:
      # Get the list of expenses
      expenses = response['Item'].get('expenses', [])
      return expenses
    else:
      return []
    

@bot.message_handler(func=lambda message: True)
def default_handler(message):
    user = message.from_user.username
    text = message.text
    value, command, note = split_3_parts(text)
    user_meta = get_user_meta_add_if_none(message.from_user.username)
    expense_categories = extract_categories(user_meta)
    if command in expense_categories:
        expense_handler(bot, user, value, command, note, message)
    elif command == "credit":
        credit_handler(bot, user, value, command, note, message)
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