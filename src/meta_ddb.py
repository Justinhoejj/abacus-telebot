import boto3
from datetime import datetime

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')  # Change to your region
meta_table = dynamodb.Table('abacus-user-meta')  # Replace with your table name

current_year_month = datetime.now().strftime("%Y-%m")
def get_user_meta_add_if_none(username):
    response = meta_table.get_item(
            Key={
                'username': username
            }
        )
    is_new_user = 'Item' not in response
    if is_new_user:
      default_meta = {
        'username': username,
        'categories': ['bills', 'food', 'commute', 'others', 'credit']
      }
      meta_table.put_item(Item=default_meta)
      return default_meta
    else:
      return response['Item']
      

def extract_categories(user_meta):
  return user_meta['categories']
  
def set_categories(username, categories_list):
  default_meta = {
      'username': username,
      'categories': categories_list
  }
  meta_table.put_item(Item=default_meta)
  return True