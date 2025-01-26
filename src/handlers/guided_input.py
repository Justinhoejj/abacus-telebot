import telebot

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import split_2_parts
from meta_ddb import get_user_meta_add_if_none, extract_categories
from accounting import expense_handler

def register_guided_input_handlers(bot: telebot.TeleBot):
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
      expense_handler(bot, message.from_user.username, value, category, note, message)
      input_handler(message) # Display buttons for next input