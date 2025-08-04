#!/usr/bin/env python3
"""
Database Setup Script via Lambda
This script invokes a Lambda function to setup the database schema instead of connecting directly.
"""

import json
import boto3
import time
import sys
from botocore.exceptions import ClientError

def invoke_setup_lambda(lambda_client, function_name, payload):
    """Invoke the database setup Lambda function"""
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        # Parse the response
        response_payload = json.loads(response['Payload'].read().decode('utf-8'))
        
        if response['StatusCode'] == 200:
            return True, response_payload
        else:
            return False, response_payload
            
    except ClientError as e:
        print(f"Error invoking Lambda function: {e}")
        return False, None

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup Redshift Database Schema via Lambda')
    parser.add_argument('--function-name', help='Lambda function name for database setup')
    parser.add_argument('--workgroup', default="tracking-workgroup", help='Redshift workgroup name')
    parser.add_argument('--namespace', default="tracking-namespace", help='Redshift namespace name')
    parser.add_argument('--secret', default="redshift-credentials", help='Secrets Manager secret name')
    parser.add_argument('--database', default="dev", help='Database name')
    parser.add_argument('--port', type=int, default=5439, help='Redshift port')
    
    args = parser.parse_args()
    
    print("🚀 Setting up Redshift Database Schema via Lambda")
    print("=" * 55)
    
    # Initialize AWS clients
    lambda_client = boto3.client('lambda')
    
    # Get Lambda function name from CloudFormation if not provided
    function_name = args.function_name
    if not function_name:
        try:
            cloudformation_client = boto3.client('cloudformation')
            response = cloudformation_client.describe_stacks(
                StackName='ELBTrackingStack'
            )
            
            outputs = response['Stacks'][0]['Outputs']
            for output in outputs:
                if output['OutputKey'] == 'SetupDatabaseFunctionName':
                    function_name = output['OutputValue']
                    break
                    
            if not function_name:
                print("❌ Could not find SetupDatabaseFunctionName in stack outputs")
                sys.exit(1)
                
        except ClientError as e:
            print(f"❌ Error getting stack outputs: {e}")
            print("Please provide --function-name parameter")
            sys.exit(1)
    
    print(f"🔧 Using Lambda function: {function_name}")
    
    # Prepare payload for Lambda
    payload = {
        'workgroup_name': args.workgroup,
        'namespace_name': args.namespace,
        'secret_name': args.secret,
        'database': args.database,
        'port': args.port
    }
    
    print("📡 Invoking database setup Lambda function...")
    print("⏳ This may take a few minutes...")
    
    # Invoke the Lambda function
    success, response = invoke_setup_lambda(lambda_client, function_name, payload)
    
    if success:
        print("✅ Database setup completed successfully!")
        if response and 'body' in response:
            body = json.loads(response['body'])
            if 'endpoint' in body:
                print(f"📊 Database endpoint: {body['endpoint']}")
            if 'database' in body:
                print(f"🗄️  Database: {body['database']}")
    else:
        print("❌ Database setup failed!")
        if response and 'body' in response:
            body = json.loads(response['body'])
            if 'error' in body:
                print(f"Error: {body['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main() 