import json
import boto3

# Initialize DynamoDB resource and specify the table
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('22bps1101_contact-manager')

def lambda_handler(event, context):
    # Get HTTP method (POST, GET, PUT, DELETE)
    http_method = event['httpMethod']
    
    # Handling POST request: Adding a new contact
    if http_method == 'POST':
        # Parse the body from a JSON string to a Python dictionary
        body = json.loads(event['body'])
        
        # Access the contact details directly from the parsed body
        first_name = body.get('firstName')
        last_name = body.get('lastName')
        phone_number = body.get('phoneNumber')
        
        if not first_name or not last_name or not phone_number:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing required fields: firstName, lastName, or phoneNumber')
            }
        
        # Prepare the item to be saved in DynamoDB
        contact_item = {
            'phoneNumber': phone_number,  # Using phone number as primary key
            'firstName': first_name,
            'lastName': last_name
        }
        
        # Add the contact to DynamoDB
        try:
            table.put_item(Item=contact_item)
            return {
                'statusCode': 200,
                'body': json.dumps(f"Contact added: {first_name} {last_name} {phone_number}")
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f"Error adding contact: {str(e)}")
            }
    
    # Handling GET request: Fetch all contacts
    elif http_method == 'GET':
        # Scan the DynamoDB table for all items (all contacts)
        try:
            response = table.scan()
            contacts = response.get('Items', [])
            return {
                'statusCode': 200,
                'body': json.dumps(contacts)
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f"Error fetching contacts: {str(e)}")
            }

    # Handling DELETE request: Delete a contact
    elif http_method == 'DELETE':
        phone_number = event['queryStringParameters']['phone_number']
        
        try:
            table.delete_item(Key={'phoneNumber': phone_number})
            return {
                'statusCode': 200,
                'body': json.dumps(f"Contact with phone number {phone_number} deleted.")
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f"Error deleting contact: {str(e)}")
            }

    # Handling PUT request: Update a contact
    elif http_method == 'PUT':
        body = json.loads(event['body'])  # Parse the body from JSON string
        
        first_name = body.get('firstName')
        last_name = body.get('lastName')
        phone_number = body.get('phoneNumber')
        
        if not first_name or not last_name or not phone_number:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing required fields: firstName, lastName, or phoneNumber')
            }
        
        # Update contact details in DynamoDB
        try:
            table.update_item(
                Key={'phoneNumber': phone_number},
                UpdateExpression="set firstName = :f, lastName = :l",
                ExpressionAttributeValues={
                    ':f': first_name,
                    ':l': last_name
                },
                ReturnValues="UPDATED_NEW"
            )
            return {
                'statusCode': 200,
                'body': json.dumps(f"Contact updated: {first_name} {last_name} {phone_number}")
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f"Error updating contact: {str(e)}")
            }

    # If method not supported
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Unsupported HTTP method')
        }
