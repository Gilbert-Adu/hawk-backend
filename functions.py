import boto3 # type: ignore
from botocore.exceptions import NoCredentialsError, PartialCredentialsError # type: ignore
from boto3.dynamodb.conditions import Attr # type: ignore
from emailer import send_email

import uuid 
import bcrypt # type: ignore
import base64
from datetime import datetime
from dotenv import load_dotenv # type: ignore
import os
load_dotenv()

# Configure DynamoDB client
dynamodb = boto3.resource('dynamodb',
                        region_name='us-east-1',
                        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                        )  # Change region as needed

# tables
table = dynamodb.Table('HawkUsers')
campaign_table = dynamodb.Table('Campaigns')
leads_table = dynamodb.Table('Leads')
payments_table = dynamodb.Table('Payments')
business_table = dynamodb.Table('Business')

RECIPIENT_EMAILS = [
    os.getenv('ADMIN_EMAIL'),
    os.getenv('SOCIAL_HAWK')
    
]
SENDER_EMAIL = "kobbyenos.770@gmail.com"
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')

def create_business(name, email, phone, businessName, businessLocation, services, shipping, fastest_reach):
    try:
        

        # Data to store in the table
        item_data = {
            'id': str(uuid.uuid4()),
            'name': name,  # Partition key
            'email': email,
            'phone': phone,
            'businessName': businessName, 
            'businessLocation': businessLocation,
            'services':services,
            'shipping': shipping,
            'fastest_reach': fastest_reach,
            'created_at': str(datetime.today().date())

        }

        # Put the item in the table
        response = business_table.put_item(Item=item_data)
        return response

    except Exception as e:
        print(f"An error occurred: {e}")


def check_password(stored_hash, password):
    stored_hashed_password = base64.b64decode(stored_hash)

    return bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password)

def create_user(name, email, password):
    try:
        # Reference the DynamoDB table
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        hashed_password_str = base64.b64encode(hashed_password).decode('utf-8')

        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('email').eq(email)
        )

        print("response: ", response)

        if len(response['Items']) > 0:
            print("user already exists")
            return {"message": "User already exists", "status":"error"}
        # Data to store in the table
        item_data = {
            'id': str(uuid.uuid4()),
            'name': name,  # Partition key
            'email': email,
            'password': hashed_password_str,
            'Subscribed': False
        }

        # Put the item in the table
        table.put_item(
            Item=item_data,
            ConditionExpression="attribute_not_exists(email)"
        )
        SUBJECT = "🤝 A NEW USER JOINED"
        BODY = f"A user named {name} created an account. Their email is {email}"

        for item in RECIPIENT_EMAILS:
            send_email(SENDER_EMAIL, SENDER_PASSWORD, item, SUBJECT, BODY)

        return item_data

    except NoCredentialsError:
        print("AWS credentials not found.")
    except PartialCredentialsError:
        print("Incomplete AWS credentials provided.")
    except Exception as e:
        print(f"An error occurred: {e}")

def login_user(email, password):
    
    response = table.scan(
        FilterExpression=Attr('email').eq(email)
    )

    #print(response)
    if 'Items' in response:
        stored_hash = response['Items'][0]['password']

        if check_password(stored_hash, password):
            return response['Items'][0]
        
        else:
            return "Invalid password"
        
    else:
        return "User not found"
    
def get_user(email):
    
    response = table.scan(
        FilterExpression=Attr('email').eq(email)
    )

    #print(response)
    if 'Items' in response:
        return response['Items'][0]
        
    else:
        return "User not found"
    
#store campaign and lead data in mongodb
def create_campaign(user_id, campaign_name, campaign_location, campaign_desc, campaign_service):



    item_data = {
            'user_id': user_id,
            'campaign_id': str(uuid.uuid4()),
            'campaign_name': campaign_name,  # Partition key
            'campaign_service': campaign_service,  # Partition key
            'campaign_location': campaign_location,
            'campaign_desc': campaign_desc,
            'created_at': str(datetime.today().date())
    }

        # Put the item in the table
    response = campaign_table.put_item(Item=item_data)
    return item_data

def get_user_campaigns(email):

    user = get_user(email)
    user_id = user['id']

    response = campaign_table.scan(
        FilterExpression=Attr('user_id').eq(user_id)
    )


    #print(response)
    if 'Items' in response:
        return response['Items']
        
    else:
        return "User not found"
    

def delete_campaign(campaign_id):
    try:
        response = campaign_table.delete_item(
            Key={
                'campaign_id': campaign_id
            }
        )
        if 'ResponseMetadata' in response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print(f"Campaign with ID '{campaign_id}' deleted successfully.")
        else:
            print(f"Failed to delete campaign with ID '{campaign_id}'.")
    except Exception as e:
        print("Error deleting item:", e)

def create_lead(user_name, campaign_name, lead_name, lead_location, lead_source, lead_post, lead_contact):
    item_data = {
            'id': str(uuid.uuid4()),
            'user_name': user_name,
            'campaign_name': campaign_name,  # Partition key
            "lead_name": lead_name,
            "lead_location": lead_location,
            'lead_source': lead_source,  # Partition key
            'lead_post': lead_post,  # Partition key
            'lead_contact': lead_contact,
            'created_at': str(datetime.today().date()),
            'message_sent': False

    }

        # Put the item in the table
    response = leads_table.put_item(Item=item_data)
    return item_data


def get_all_users():
    # Fetch all items using scan()
    try:
        response = table.scan()
        items = response.get('Items', [])

        return items
    except Exception as e:
        print("Error fetching data from DynamoDB:", e)
        return []
    
#total leads
 
def total_leads(email):
    
    response = leads_table.scan(
        FilterExpression=Attr('user_name').eq(email)
    )

    #print(response)
    if 'Items' in response:
        return response['Items']
        
    else:
        return "User not found"
    
#delete leads
def delete_leads(campaign_name):
    # Query the table to find the item by campaign_name
    response = leads_table.scan(
        FilterExpression=Attr('campaign_name').eq(campaign_name)
    )

    items = response.get('Items', [])
    
    if not items:
        print(f"No item found with campaign_name: {campaign_name}")
        return

    # Delete each matching item
    for item in items:
        partition_key_value = item['id']  # Replace with your partition key attribute name
        print(f"Deleting item with partition key: {partition_key_value}")
        
        leads_table.delete_item(
            Key={
                'id': partition_key_value  # Replace with your partition key name
            }
        )
        print("Item deleted successfully")


def change_payment_status(email, status):
        # Step 1: Scan the table to find the user by email (inefficient without a GSI)
    response = table.scan(
        FilterExpression='email = :email',
        ExpressionAttributeValues={':email': email}
    )

    # Check if any item was found
    items = response.get('Items', [])
    if not items:
        print("User not found.")
        return

    # Assuming email is unique, get the first matching item
    item = items[0]
    partition_key_value = item['id']

    # Step 2: Update the subscribed field
    table.update_item(
        Key={'id': partition_key_value},
        UpdateExpression='SET Subscribed = :Subscribed',
        ExpressionAttributeValues={':Subscribed': status}
    )

    payments_data = {
            'id': str(uuid.uuid4()),
            'user_email': email,
            'status': status,  # Partition key
            'created_at': str(datetime.today().date()),

    }

        # Put the item in the table
    payments_response = payments_table.put_item(Item=payments_data)
    print("User subscription updated successfully.")
    return response





 





    