#!/bin/bash

# CDK Deployment Script for Tracking Lambda
# This script handles the complete deployment of the AWS infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="ElbTrackingStack"
REGION=${AWS_DEFAULT_REGION:-"eu-central-1"}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo -e "${BLUE}🚀 CDK Deployment Script for Tracking Lambda${NC}"
echo -e "${BLUE}=============================================${NC}"
echo -e "Stack Name: ${GREEN}$STACK_NAME${NC}"
echo -e "Region: ${GREEN}$REGION${NC}"
echo -e "Account ID: ${GREEN}$ACCOUNT_ID${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check AWS CLI configuration
check_aws_config() {
    echo -e "${YELLOW}🔍 Checking AWS configuration...${NC}"
    
    if ! command_exists aws; then
        echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
        exit 1
    fi
    
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        echo -e "${RED}❌ AWS CLI is not configured. Please run 'aws configure' first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ AWS CLI is properly configured${NC}"
}

# Function to check Node.js and npm
check_node_requirements() {
    echo -e "${YELLOW}🔍 Checking Node.js requirements...${NC}"
    
    if ! command_exists node; then
        echo -e "${RED}❌ Node.js is not installed. Please install it first.${NC}"
        exit 1
    fi
    
    if ! command_exists npm; then
        echo -e "${RED}❌ npm is not installed. Please install it first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Node.js and npm are available${NC}"
}

# Function to install dependencies
install_dependencies() {
    echo -e "${YELLOW}📦 Installing CDK dependencies...${NC}"
    
    if [ ! -d "node_modules" ]; then
        npm install
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    else
        echo -e "${GREEN}✅ Dependencies already installed${NC}"
    fi
}

# Function to build the project
build_project() {
    echo -e "${YELLOW}🔨 Building CDK project...${NC}"
    npm run build
    echo -e "${GREEN}✅ Project built successfully${NC}"
}

# Function to bootstrap CDK (if needed)
bootstrap_cdk() {
    echo -e "${YELLOW}🚀 Bootstrapping CDK (if needed)...${NC}"
    
    if ! aws cloudformation describe-stacks --stack-name CDKToolkit >/dev/null 2>&1; then
        echo -e "${YELLOW}CDK bootstrap not found. Bootstrapping...${NC}"
        npx cdk bootstrap
        echo -e "${GREEN}✅ CDK bootstrapped successfully${NC}"
    else
        echo -e "${GREEN}✅ CDK already bootstrapped${NC}"
    fi
}

# Function to deploy the stack
deploy_stack() {
    echo -e "${YELLOW}🚀 Deploying CDK stack...${NC}"
    
    # Check if stack exists
    if aws cloudformation describe-stacks --stack-name $STACK_NAME >/dev/null 2>&1; then
        echo -e "${YELLOW}Stack exists. Updating...${NC}"
        npx cdk deploy --require-approval never
    else
        echo -e "${YELLOW}Stack doesn't exist. Creating...${NC}"
        npx cdk deploy --require-approval never
    fi
    
    echo -e "${GREEN}✅ Stack deployed successfully${NC}"
}

# Function to get stack outputs
get_outputs() {
    echo -e "${YELLOW}📋 Getting stack outputs...${NC}"
    
    # Get API Gateway URL
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query "Stacks[0].Outputs[?OutputKey=='ApiGatewayUrl'].OutputValue" \
        --output text)
    
    # Get Lambda function name
    LAMBDA_NAME=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query "Stacks[0].Outputs[?OutputKey=='LambdaFunctionName'].OutputValue" \
        --output text)
    
    # Get Redshift secret name
    SECRET_NAME=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query "Stacks[0].Outputs[?OutputKey=='RedshiftSecretName'].OutputValue" \
        --output text)
    
    # Get Redshift namespace
    REDSHIFT_NAMESPACE=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query "Stacks[0].Outputs[?OutputKey=='RedshiftNamespace'].OutputValue" \
        --output text)
    
    # Get Redshift workgroup
    REDSHIFT_WORKGROUP=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query "Stacks[0].Outputs[?OutputKey=='RedshiftWorkgroup'].OutputValue" \
        --output text)
    
    # Get Redshift endpoint
    REDSHIFT_ENDPOINT=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query "Stacks[0].Outputs[?OutputKey=='RedshiftEndpoint'].OutputValue" \
        --output text)
    
    echo -e "${GREEN}✅ Stack outputs:${NC}"
    echo -e "  API Gateway URL: ${BLUE}$API_URL${NC}"
    echo -e "  Lambda Function: ${BLUE}$LAMBDA_NAME${NC}"
    echo -e "  Redshift Secret: ${BLUE}$SECRET_NAME${NC}"
    echo -e "  Redshift Namespace: ${BLUE}$REDSHIFT_NAMESPACE${NC}"
    echo -e "  Redshift Workgroup: ${BLUE}$REDSHIFT_WORKGROUP${NC}"
    echo -e "  Redshift Endpoint: ${BLUE}$REDSHIFT_ENDPOINT${NC}"
}

# Function to test the deployment
test_deployment() {
    echo -e "${YELLOW}🧪 Testing deployment...${NC}"
    
    # Get API Gateway URL
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query "Stacks[0].Outputs[?OutputKey=='ApiGatewayUrl'].OutputValue" \
        --output text)
    
    if [ -z "$API_URL" ]; then
        echo -e "${RED}❌ Could not get API Gateway URL${NC}"
        return 1
    fi
    
    # Test data
    TEST_DATA='{
        "event": "page view",
        "data": {
            "domain": "www.example.com",
            "title": "Website Title",
            "referrer": "https://www.google.com/",
            "search": "",
            "id": "/"
        },
        "context": {},
        "globals": {
            "pagetype": "unknown"
        },
        "custom": {},
        "user": {
            "session": "mbb0ai263mbp"
        },
        "nested": [],
        "consent": {
            "analytics": true
        },
        "id": "1752140468984-9h6lhh-2",
        "trigger": "load",
        "entity": "page",
        "action": "view",
        "timestamp": 1752140468984,
        "timing": 3.44,
        "group": "9h6lhh",
        "count": 2,
        "version": {
            "source": "3.4.2",
            "tagging": "1"
        },
        "source": {
            "type": "web",
            "id": "https://www.example.com/",
            "previous_id": "https://www.google.com/"
        }
        }'
    
    echo -e "${YELLOW}Testing API Gateway endpoint: $API_URL${NC}"
    
    # Test the endpoint
    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -d "$TEST_DATA" \
        "$API_URL")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ API Gateway test successful${NC}"
        echo -e "Response: $BODY"
    else
        echo -e "${RED}❌ API Gateway test failed (HTTP $HTTP_CODE)${NC}"
        echo -e "Response: $BODY"
    fi
}

# Function to show stack status
show_status() {
    echo -e "${YELLOW}📊 Stack status:${NC}"
    npx cdk list
    echo ""
    
    # Show CloudFormation stack status
    STACK_STATUS=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query "Stacks[0].StackStatus" \
        --output text 2>/dev/null || echo "STACK_NOT_FOUND")
    
    echo -e "Stack Status: ${BLUE}$STACK_STATUS${NC}"
}

# Function to destroy the stack
destroy_stack() {
    echo -e "${YELLOW}🗑️  Destroying CDK stack...${NC}"
    
    read -p "Are you sure you want to destroy the stack? This will delete all resources. (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        npx cdk destroy --force
        echo -e "${GREEN}✅ Stack destroyed successfully${NC}"
    else
        echo -e "${YELLOW}❌ Destruction cancelled${NC}"
    fi
}

# Function to show logs
show_logs() {
    echo -e "${YELLOW}📋 Showing Lambda logs...${NC}"
    
    # Get Lambda function name
    LAMBDA_NAME=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query "Stacks[0].Outputs[?OutputKey=='LambdaFunctionName'].OutputValue" \
        --output text)
    
    if [ -n "$LAMBDA_NAME" ]; then
        echo -e "Showing logs for Lambda function: ${BLUE}$LAMBDA_NAME${NC}"
        aws logs tail "/aws/lambda/$LAMBDA_NAME" --follow
    else
        echo -e "${RED}❌ Could not get Lambda function name${NC}"
    fi
}

# Function to setup database schema
setup_database() {
    echo -e "${YELLOW}🏗️  Setting up database schema via Lambda...${NC}"
    
    # Check if Python and required packages are available
    if ! command_exists python3; then
        echo -e "${RED}❌ Python3 is not installed. Please install it first.${NC}"
        return 1
    fi
    
    # Check if required packages are available
    if ! python3 -c "import boto3" 2>/dev/null; then
        echo -e "${YELLOW}📦 Installing required Python packages...${NC}"
        pip3 install boto3 botocore
    fi
    
    # Get stack outputs
    SECRET_NAME=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query "Stacks[0].Outputs[?OutputKey=='RedshiftSecretName'].OutputValue" \
        --output text)
    
    REDSHIFT_NAMESPACE=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query "Stacks[0].Outputs[?OutputKey=='RedshiftNamespaceOutput'].OutputValue" \
        --output text)
    
    REDSHIFT_WORKGROUP=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query "Stacks[0].Outputs[?OutputKey=='RedshiftWorkgroupOutput'].OutputValue" \
        --output text)
    
    SETUP_FUNCTION_NAME=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --query "Stacks[0].Outputs[?OutputKey=='SetupDatabaseFunctionName'].OutputValue" \
        --output text)
    
    if [ -z "$SECRET_NAME" ] || [ -z "$REDSHIFT_NAMESPACE" ] || [ -z "$REDSHIFT_WORKGROUP" ] || [ -z "$SETUP_FUNCTION_NAME" ]; then
        echo -e "${RED}❌ Could not get required stack outputs${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Stack outputs retrieved:${NC}"
    echo -e "  Redshift Secret: ${BLUE}$SECRET_NAME${NC}"
    echo -e "  Redshift Namespace: ${BLUE}$REDSHIFT_NAMESPACE${NC}"
    echo -e "  Redshift Workgroup: ${BLUE}$REDSHIFT_WORKGROUP${NC}"
    echo -e "  Setup Function: ${BLUE}$SETUP_FUNCTION_NAME${NC}"
    
    # Run the database setup script via Lambda
    echo -e "${YELLOW}🚀 Running database setup via Lambda function...${NC}"
    
    if [ -f "setup-database-via-lambda.py" ]; then
        python3 setup-database-via-lambda.py \
            --function-name "$SETUP_FUNCTION_NAME" \
            --workgroup "$REDSHIFT_WORKGROUP" \
            --namespace "$REDSHIFT_NAMESPACE" \
            --secret "$SECRET_NAME" \
            --database "dev" \
            --port 5439
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Database setup completed successfully${NC}"
        else
            echo -e "${RED}❌ Database setup failed${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ setup-database-via-lambda.py not found in current directory${NC}"
        return 1
    fi
}

# Function to show help
show_help() {
    echo -e "${BLUE}Usage: $0 [COMMAND]${NC}"
    echo ""
    echo "Commands:"
    echo "  deploy     - Deploy the CDK stack (default)"
    echo "  destroy    - Destroy the CDK stack"
    echo "  status     - Show stack status"
    echo "  test       - Test the deployment"
    echo "  logs       - Show Lambda logs"
    echo "  database   - Setup database schema"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 destroy"
    echo "  $0 test"
    echo "  $0 database"
    echo ""
    echo "Database Setup:"
echo "  The database command will:"
echo "  - Install required Python dependencies"
echo "  - Get Redshift connection details from stack outputs"
echo "  - Invoke a Lambda function to create the events table with proper indexes"
echo "  - No direct network access to Redshift required"
}

# Main execution
main() {
    local command=${1:-deploy}
    
    case $command in
        deploy)
            check_aws_config
            check_node_requirements
            install_dependencies
            build_project
            bootstrap_cdk
            deploy_stack
            get_outputs
            setup_database
            echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
            ;;
        destroy)
            check_aws_config
            check_node_requirements
            install_dependencies
            destroy_stack
            ;;
        status)
            check_aws_config
            check_node_requirements
            install_dependencies
            show_status
            ;;
        test)
            check_aws_config
            test_deployment
            ;;
        logs)
            check_aws_config
            show_logs
            ;;
        database)
            check_aws_config
            setup_database
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $command${NC}"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 