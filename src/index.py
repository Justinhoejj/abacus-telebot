import os
import telebot
import boto3
from datetime import datetime
from decimal import Decimal
import json
import csv, io

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')  # Change to your region
ledger_table = dynamodb.Table('abacus-ledger')  # Replace with your table name

# Bot token from environment variable
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded = False)

expense_categories = set(['bills', 'food', 'commute', 'others', 'credit'])
current_year_month = datetime.now().strftime("%Y-%m")

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

def is_valid_number(s):
    try:
        # Attempt to convert to float (works for both integers and floats)
        float(s)
        return True
    except ValueError:
        return False

@bot.message_handler(commands=['report'])
def report_handler(message):
    expenses = get_expenses(message.from_user.username, current_year_month)
    total = sum(float(expense["value"]) for expense in expenses)
    bot.send_message(message.chat.id, f"you've spend {total} this month.")

def split_3_parts(text):
    parts = text.split(maxsplit=2)
    if len(parts) == 1:
        return parts[0], "", "" 
    elif len(parts) == 2:
        return parts[0], parts[1], ""
    else:
        return parts[0], parts[1], parts[2]

def save_to_ledger(user, category, value, desc):
    new_expense = {"value": value, "category": category, "notes": desc}
    new_expense = json.loads(json.dumps(new_expense), parse_float=Decimal)
    updated_expenses = []
    try:
        response = get_record_from_ledger(user, current_year_month)
        if 'Item' in response:
            existing_item = response['Item']
            existing_expenses = existing_item.get('expenses', [])
            updated_expenses.extend(existing_expenses)
        
        updated_expenses.append(new_expense)
        # If the item doesn't exist, save the new record
        updated_item = {
            'username': user,
            'year_month': current_year_month,
            'expenses': updated_expenses
        }
        # Insert the new item
        ledger_table.put_item(Item=updated_item)
        return "Record inserted successfully."
    except Exception as e:
        print(f"Save ledger Error: {e}")
        return f"Error: {str(e)}"
    
@bot.message_handler(commands=['category'])
def category_command(message):
    bot.send_message(message.chat.id, f"Valid category are [bills, food, commute, others, credit]")

@bot.message_handler(commands=["help"])
def help_command(message):
    bot.reply_to(message, "All accounting commands take the form '<value> <category> <optional notes>'. For example: 9.45 food mc spicy. /category to see all valid accounting category.")

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
      
def get_record_from_ledger(username, year_month):
  try:
    response = ledger_table.get_item(
            Key={
                'username': username,
                'year_month': year_month
            }
        )
    return response
  except:
    raise ValueError("Unable to get expenses from DDB")

def generate_doc(data):
    """
    csv module can write data in io.StringIO buffer only, python-telegram-bot library can send files 
    only from io.BytesIO bufferwe need to convert StringIO to BytesIO, extract csv-string, convert 
    it to bytes and write to buffer.
    """
    
    string_buffer = io.StringIO()
    csv.writer(string_buffer).writerows(data)
    string_buffer.seek(0)

    bytes_buffer = io.BytesIO()
    bytes_buffer.write(string_buffer.getvalue().encode())
    bytes_buffer.seek(0)

    # set a filename with file's extension
    bytes_buffer.name = f'spending_report.csv'
    return bytes_buffer
    
@bot.message_handler(func=lambda message: True)
def default_handler(message):
    user = message.from_user.username
    text = message.text
    value, command, note = split_3_parts(text)
    if command in expense_categories:
        expense_handler(user, value, command, note, message)
    elif command == "credit":
        credit_handler(user, value, command, note, message)
    else:
        bot.send_message(message.chat.id, "invalid command")

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