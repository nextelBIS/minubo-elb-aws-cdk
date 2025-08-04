import json
import logging
import os
import pg8000
from datetime import datetime
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS Secrets Manager client
secrets_client = boto3.client('secretsmanager')

def get_redshift_credentials():
    """Retrieve Redshift credentials from AWS Secrets Manager"""
    try:
        secret_name = os.environ.get('REDSHIFT_SECRET_NAME')
        if not secret_name:
            raise ValueError("REDSHIFT_SECRET_NAME environment variable not set")

        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])

        return {
            'host': secret['host'],
            'port': secret['port'],
            'database': secret['database'],
            'user': secret['username'],
            'password': secret['password']
        }
    except Exception as e:
        logger.error(f"Error retrieving Redshift credentials: {str(e)}")
        raise

def get_redshift_connection():
    """Create and return a Redshift connection with SSL"""
    try:
        credentials = get_redshift_credentials()
        # Add SSL configuration
        credentials['ssl_context'] = True
        connection = pg8000.Connection(**credentials)
        return connection
    except Exception as e:
        logger.error(f"Error connecting to Redshift: {str(e)}")
        raise

def extract_data_fields(data: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """Extract specific fields from the data object"""
    return {
        'data_id': data.get('id'),
        'data_device': data.get('device'),
        'data_marketing': data.get('marketing'),
        'data_source': data.get('source'),
        'data_medium': data.get('medium'),
        'data_campaign': data.get('campaign'),
        'data_clickId': data.get('clickId'),
        'data_term': data.get('term'),
        'data_referrer': data.get('referrer'),
        'data_storage': data.get('storage'),
        'data_isNew': data.get('isNew'),
        'data_count': data.get('count'),
        'data_order_id': data.get('order_id'),
        'data_domain': data.get('domain')
    }

def extract_user_fields(user: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """Extract specific fields from the user object"""
    return {
        'user_device': user.get('device'),
        'user_session': user.get('session')
    }

def extract_source_fields(source: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """Extract specific fields from the source object"""
    return {
        'source_id': source.get('id'),
        'source_previous_id': source.get('previous_id')
    }

def convert_timestamp(timestamp_ms: int) -> str:
    """Convert millisecond timestamp to ISO format string"""
    try:
        dt = datetime.fromtimestamp(timestamp_ms / 1000.0)
        return dt.isoformat()
    except Exception as e:
        logger.error(f"Error converting timestamp {timestamp_ms}: {str(e)}")
        return datetime.now().isoformat()

def insert_event_to_redshift(event_data: Dict[str, Any]) -> bool:
    """Insert event data into Redshift table"""
    try:
        connection = get_redshift_connection()
        cursor = connection.cursor()

        # Extract timestamp
        timestamp = convert_timestamp(event_data.get('timestamp', 0))

        # Extract data fields
        data_fields = extract_data_fields(event_data.get('data', {}))

        # Extract user fields
        user_fields = extract_user_fields(event_data.get('user', {}))

        # Extract source fields
        source_fields = extract_source_fields(event_data.get('source', {}))

        # Prepare the INSERT statement
        insert_query = """
        INSERT INTO events (
            timestamp, event, data, data_id, data_device, data_marketing,
            data_source, data_medium, data_campaign, data_clickId, data_term,
            data_referrer, data_storage, data_isNew, data_count, data_order_id,
            data_domain, context, custom, globals, "user", user_device, user_session,
            nested, consent, event_id, trigger, entity, action, timing, "group", count,
            version, source, source_id, source_previous_id
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s
        )
        """

        # Prepare values
        values = (
            timestamp,  # timestamp
            event_data.get('event'),  # event
            json.dumps(event_data.get('data', {})),  # data
            data_fields['data_id'],  # data_id
            data_fields['data_device'],  # data_device
            data_fields['data_marketing'],  # data_marketing
            data_fields['data_source'],  # data_source
            data_fields['data_medium'],  # data_medium
            data_fields['data_campaign'],  # data_campaign
            data_fields['data_clickId'],  # data_clickId
            data_fields['data_term'],  # data_term
            data_fields['data_referrer'],  # data_referrer
            data_fields['data_storage'],  # data_storage
            data_fields['data_isNew'],  # data_isNew
            data_fields['data_count'],  # data_count
            data_fields['data_order_id'],  # data_order_id
            data_fields['data_domain'],  # data_domain
            json.dumps(event_data.get('context', {})),  # context
            json.dumps(event_data.get('custom', {})),  # custom
            json.dumps(event_data.get('globals', {})),  # globals
            json.dumps(event_data.get('user', {})),  # user
            user_fields['user_device'],  # user_device
            user_fields['user_session'],  # user_session
            json.dumps(event_data.get('nested', [])),  # nested
            json.dumps(event_data.get('consent', {})),  # consent
            event_data.get('id'),  # event_id
            event_data.get('trigger'),  # trigger
            event_data.get('entity'),  # entity
            event_data.get('action'),  # action
            event_data.get('timing'),  # timing
            event_data.get('group'),  # group
            event_data.get('count'),  # count
            json.dumps(event_data.get('version', {})),  # version
            json.dumps(event_data.get('source', {})),  # source
            source_fields['source_id'],  # source_id
            source_fields['source_previous_id']  # source_previous_id
        )

        cursor.execute(insert_query, values)
        connection.commit()

        cursor.close()
        connection.close()

        logger.info(f"Successfully inserted event with ID: {event_data.get('id')}")
        return True

    except Exception as e:
        logger.error(f"Error inserting event to Redshift: {str(e)}")
        if 'connection' in locals():
            connection.rollback()
            connection.close()
        return False

def lambda_handler(event, context):
    """AWS Lambda handler function"""
    try:
        # Log the incoming event
        logger.info(f"Received event: {json.dumps(event)}")

        # Parse the request body
        if 'body' not in event:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({'error': 'Missing request body'})
            }

        # Parse JSON body
        try:
            event_data = json.loads(event['body'])
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request body: {str(e)}")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({'error': 'Invalid JSON in request body'})
            }

        # Validate required fields
        required_fields = ['event', 'timestamp']
        missing_fields = [field for field in required_fields if field not in event_data]

        if missing_fields:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({'error': f'Missing required fields: {missing_fields}'})
            }

        # Insert event to Redshift
        success = insert_event_to_redshift(event_data)

        if success:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({
                    'message': 'Event processed successfully',
                    'event_id': event_data.get('id')
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({'error': 'Failed to process event'})
            }

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({'error': 'Internal server error'})
        } 