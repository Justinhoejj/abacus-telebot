from datetime import datetime

perm_expense_categories = set(['bills', 'food', 'commute', 'others', 'credit'])
category_emojis = {
    "bills": "💡",
    "food": "🍔",
    "groceries": "🛒",
    "commute": "🚗"
}
current_year_month = datetime.now().strftime("%Y-%m") # Clean up duplicate declaration in ledger_ddb
