import telebot
import csv, io

from accounting import get_expenses
from variables import current_year_month

def register_export_handlers(bot: telebot.TeleBot):
  @bot.message_handler(commands=['export'])
  def export_command(message):
      expenses = get_expenses(message.from_user.username, current_year_month)
      if len(expenses) == 0:
          bot.send_message(message.chat.id, "you didnt spend shit this month")
      else:
          data = [["category", "value", "notes"]] # Add headers
          data += [[expense['category'], expense['value'], expense['notes']] for expense in expenses]
          bot.send_document(message.chat.id, document=generate_doc(data))
          
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