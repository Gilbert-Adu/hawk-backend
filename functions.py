import boto3 # type: ignore
from botocore.exceptions import NoCredentialsError, PartialCredentialsError # type: ignore
from boto3.dynamodb.conditions import Attr # type: ignore

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


        # Data to store in the table
        item_data = {
            'id': str(uuid.uuid4()),
            'name': name,  # Partition key
            'email': email,
            'password': hashed_password_str,
            'Subscribed': False
        }

        # Put the item in the table
        response = table.put_item(Item=item_data)
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
    except Exception as