import boto3
from decimal import Decimal
import json
from datetime import datetime

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')  # Change to your region
ledger_table = dynamodb.Table('abacus-ledger')  # Replace with your table name

current_year_month = datetime.now().strftime("%Y-%m")
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