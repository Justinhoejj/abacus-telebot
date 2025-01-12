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
        'categories': ['bills', 'commute', 'food', 'others', 'credit'],
        'joinedAtEpoch': int(datetime.now().timestamp()) 
      }
      meta_table.put_item(Item=default_meta)
      return default_meta
    else:
      return response['Item']
      

def extract_categories(user_meta):
  return user_meta['categories']
  
def set_categories(username, category):
  category = category.lower()
  user_meta = get_user_meta_add_if_none(username)
  categories = extract_categories(user_meta)
  if category not in categories:
      categories.append(category)
  categories.remove('credit')
  categories.sort()  
  categories.append('credit')  # Add 'credit' back to the end

  user_meta['categories'] = categories
  meta_table.put_item(Item=user_meta)
  
  return True

def remove_category(username, category):
    category = category.lower()
    user_meta = get_user_meta_add_if_none(username)
    categories = extract_categories(user_meta)
    if category in categories:
      categories.remove(category)
    user_meta['categories'] = categories
    meta_table.put_item(Item=user_meta)