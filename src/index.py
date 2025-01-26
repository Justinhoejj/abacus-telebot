import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

from ledger_ddb import save_to_ledger, get_record_from_ledger
from meta_ddb import get_user_meta_add_if_none, extract_categories
from utils import is_valid_number, split_2_parts, split_3_parts, generate_doc
from handlers import category
# Bot token from environment variable
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded = False)

category.register_category_handlers(bot)

perm_expense_categories = set(['bills', 'food', 'commute', 'others', 'credit'])
category_emojis = {
    "bills": "💡",
    "food": "🍔",
    "groceries": "🛒",
    "commute": "🚗"
}
current_year_month = datetime.now().strftime("%Y-%m") # Clean up duplicate declaration in ledger_ddb

def expense_handler(user, value, command, note, message):
    if not is_valid_number(value):
        bot.reply_to(message, f"Dumbass you gotta tell me how much you spent")
    else:
        category = command
        bot.reply_to(message, f"Got it {message.from_user.first_name}, you spent ${value} on {category}.")
        save_to_ledger(user, category, value, note)

def credit_handler(user, value, command, note, message):
    if not is_valid_number(value):
        bot.reply_to(message, f"Dumbass you gotta tell me how much you wanna credit")
    else:
        category = command
        bot.reply_to(message, f"Got it {message.from_user.first_name}, you wanna credit ${value}.")
        save_to_ledger(user, category, float(value) * - 1, note)
    
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

@bot.message_handler(commands=['input'])
def input_handler(message):
    """
    Handles the /input command by showing a list of expense categories as buttons.
    """
    chat_id = message.chat.id
    markup = InlineKeyboardMarkup()
    
    user_meta = get_user_meta_add_if_none(message.from_user.username)
    expense_categories = extract_categories(user_meta)
    
    # Add buttons for each category
    for category in expense_categories:
        markup.add(InlineKeyboardButton(category.capitalize(), callback_data=f"category_{category}"))
    
    bot.send_message(chat_id, "Select an expense category to log when ready:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
def category_selected_handler(call):
    """
    Handles the category selection from the inline keyboard buttons.
    """
    chat_id = call.message.chat.id
    category = call.data.split("_")[1]  # Extract category from callback data

    # Prompt user for the expense value, include category in the message
    bot.send_message(
        chat_id,
        # Coupled to expense_value_handler careful when modifying
        f"*{category}* selected. Enter amount followed by optional notes (eg. \"4.20 train to Busan\"):", 
        parse_mode="Markdown",
        reply_markup=telebot.types.ForceReply(selective=True),  # Force reply
    )
    bot.answer_callback_query(call.id)  # Acknowledge callback


@bot.message_handler(func=lambda message: message.reply_to_message and "selected. Enter amount followed by optional notes" in message.reply_to_message.text)
def expense_value_handler(message):
    """
    Handles the input of the expense value after the category is selected.
    """
    # Extract the category from the reply-to message
    category = message.reply_to_message.text.split("selected")[0].strip()  # Extract the category name from the prompt
    # Validate the entered value
    value, note = split_2_parts(message.text.strip())
    if category == "credit":
      credit_handler(message.from_user.username, value, category, note, message)
    else:
      expense_handler(message.from_user.username, value, category, note, message)
    input_handler(message) # Display buttons for next input
    

@bot.message_handler(func=lambda message: True)
def default_handler(message):
    user = message.from_user.username
    text = message.text
    value, command, note = split_3_parts(text)
    user_meta = get_user_meta_add_if_none(message.from_user.username)
    expense_categories = extract_categories(user_meta)
    if command in expense_categories:
        expense_handler(user, value, command, note, message)
    elif command == "credit":
        credit_handler(user, value, command, note, message)
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