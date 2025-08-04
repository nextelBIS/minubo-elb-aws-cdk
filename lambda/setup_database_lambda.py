#!/usr/bin/env python3
"""
Lambda Function for Database Setup
This Lambda function creates the necessary tables and users for the tracking Lambda function.
"""

import json
import boto3
import pg8000
import time
import sys
import os
from botocore.exceptions import ClientError

def get_redshift_credentials(secret_name):
    """Get Redshift credentials from Secrets Manager"""
    # Get region from environment or default to eu-central-1
    region = os.environ.get('AWS_REGION', 'eu-central-1')
    secrets_client = boto3.client('secretsmanager', region_name=region)
    
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        return secret
    except ClientError as e:
        print(f"Error getting Redshift credentials: {e}")
        print(f"Region: {region}, Secret: {secret_name}")
        return None

def create_database_schema(host, port, database, username, password):
    """Create the database schema"""
    try:
        # Connect to Redshift with SSL
        conn = pg8000.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password,
            ssl_context=True
        )
        
        cursor = conn.cursor()
        
        # Create events table
        create_events_table = """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER IDENTITY(1,1) PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            event VARCHAR(255) NOT NULL,
            data TEXT,
            data_id VARCHAR(255),
            data_device VARCHAR(255),
            data_marketing TEXT,
            data_source VARCHAR(255),
            data_medium VARCHAR(255),
            data_campaign VARCHAR(255),
            data_clickId VARCHAR(255),
            data_term VARCHAR(255),
            data_referrer VARCHAR(500),
            data_storage VARCHAR(255),
            data_isNew BOOLEAN,
            data_count INTEGER,
            data_order_id VARCHAR(255),
            data_domain VARCHAR(255),
            context TEXT,
            custom TEXT,
            globals TEXT,
            "user" TEXT,
            user_device VARCHAR(255),
            user_session VARCHAR(255),
            nested TEXT,
            consent TEXT,
            event_id VARCHAR(255),
            trigger VARCHAR(255),
            entity VARCHAR(255),
            action VARCHAR(255),
            timing VARCHAR(255),
            "group" VARCHAR(255),
            count INTEGER,
            version TEXT,
            source TEXT,
            source_id VARCHAR(255),
            source_previous_id VARCHAR(255),
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_events_table)
        print("✅ Events table created successfully") 
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Database schema setup completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database schema: {e}")
        return False

def lambda_handler(event, context):
    """Lambda handler for database setup"""
    print("🚀 Starting database setup process")
    
    # Configuration
    secret_name = os.environ.get('REDSHIFT_SECRET_NAME', 'redshift-credentials')
    
    # Get credentials from secret (which now includes the static endpoint)
    print(f"🔐 Getting credentials from Secrets Manager: {secret_name}")
    credentials = get_redshift_credentials(secret_name)
    
    if not credentials:
        error_msg = "Failed to get Redshift credentials"
        print(f"❌ {error_msg}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': error_msg})
        }
    
    print("✅ Credentials retrieved successfully")
    print(f"📡 Using endpoint: {credentials.get('host')}")
    
    # Wait for Redshift to be ready
    #print("⏳ Waiting for Redshift to be ready...")
    #time.sleep(30)  # Give Redshift time to be fully ready
    
    # Create database schema
    print("🏗️  Creating database schema...")
    print(credentials)
    print("password: ", credentials.get('password'))

    success = create_database_schema(
        host=credentials.get('host'),
        port=credentials.get('port', 5439),
        database=credentials.get('database', 'dev'),
        username=credentials.get('username', 'admin'),
        password=credentials.get('password')
    )
    
    if success:
        print("🎉 Database setup completed successfully!")
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Database setup completed successfully',
                'endpoint': credentials.get('host'),
                'database': credentials.get('database', 'dev')
            })
        }
    else:
        error_msg = "Database setup failed"
        print(f"❌ {error_msg}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': error_msg})
        } 