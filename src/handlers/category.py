import telebot

from meta_ddb import set_categories, remove_category
from utils import is_valid_word
from variables import perm_expense_categories

def register_category_handlers(bot: telebot.TeleBot):
  @bot.message_handler(commands=['add_category'])
  def add_category_handler(message):
    bot.reply_to(message, f"Category name?", reply_markup=telebot.types.ForceReply(selective=True))

  @bot.message_handler(func=lambda message: message.reply_to_message and "Category name?" in message.reply_to_message.text)
  def add_category_respond(message):
    category = message.text
    if is_valid_word(message.text):
      set_categories(message.from_user.username, category)
      bot.reply_to(message, f"Added {category} to expense category.")
    else:
      bot.reply_to(message, f"Category has to be a single word")

  @bot.message_handler(commands=['remove_category'])
  def remove_category_handler(message):
    bot.reply_to(message, f"Category to delete?", reply_markup=telebot.types.ForceReply(selective=True))

  @bot.message_handler(func=lambda message: message.reply_to_message and "Category to delete?" in message.reply_to_message.text)
  def remove_category_respond(message):
    category = message.text
    if is_valid_word(category):
      if category.lower() in perm_expense_categories:
        bot.reply_to(message, f"Provided category cannot be removed.")
      else: 
        remove_category(message.from_user.username, category)
        bot.reply_to(message, f"Removed {category} from expense category.")
    else:
      bot.reply_to(message, f"Category has to be a single word")