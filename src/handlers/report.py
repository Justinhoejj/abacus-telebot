import telebot
from variables import current_year_month, category_emojis
from accounting import get_expenses

def register_report_handlers(bot: telebot.TeleBot):
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

      report = f"💰 *Expense Breakdown ({current_year_month}):*\n"
      for category, value in aggregated.items():
          emoji = category_emojis.get(category, "🎮")
          percentage = (value / total_spend) * 100
          report += f"  - {emoji} *{category.capitalize()}*: ${value:.2f} ({percentage:.2f}%)\n"
      
      report += f"\n*Total Expense*: ${total_spend:.2f}"
      report += f"\n*Total Credit*: ${total_credit:.2f}"
      report += f"\n📊 *Nett spending*: ${(total_spend+total_credit):.2f}\n\n"
      bot.send_message(message.chat.id, report, parse_mode="Markdown")