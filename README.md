# Tracking Lambda CDK Infrastructure

AWS CDK infrastructure for a tracking Lambda function with API Gateway and Redshift Serverless integration.

## 🏗️ Architecture

- **Lambda Function**: Python 3.9 runtime with Redshift connectivity
- **API Gateway**: REST API with CORS support
- **Redshift Serverless**: Namespace and workgroup for data storage
- **VPC & Security Groups**: Network configuration for Lambda-Redshift connectivity
- **Secrets Manager**: Secure storage for Redshift credentials
- **CloudWatch**: Monitoring and logging

## 📁 Project Structure

```
cdk/
├── bin/
│   └── tracking-lambda-cdk.ts      # CDK app entry point
├── lib/
│   └── elb-tracking-stack.ts       # Main infrastructure stack
├── lambda/
│   ├── lambda_function.py          # Lambda function code
│   └── requirements.txt            # Python dependencies
|   └── setup_database_lambda.py    # Lambda code to create the database table
├── setup-database.py               # Database schema setup script
├── deploy.sh                       # Deployment script
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites

- AWS CLI configured
- Node.js (v20+) and npm
- AWS CDK (installed automatically)

### Domain Setup Prerequisites

**⚠️ IMPORTANT: Complete these steps BEFORE deploying the stack**

1. **Create a Hosted Zone for your subdomain** (e.g., `mnb.yourdomain.com`):
   - Go to AWS Route 53 Console
   - Create a new hosted zone for your subdomain
   - Note the hosted zone ID (e.g., `Z04627343E8DYMW1I6O6C`)

2. **Request an SSL Certificate**:
   - Go to AWS Certificate Manager (ACM)
   - Request a certificate for your subdomain (e.g., `mnb.yourdomain.com`)
   - Validate the certificate using DNS validation
   - Ensure the certificate is in the same region as your stack


### Installation & Deployment

```bash
# Navigate to CDK directory
cd cdk

# Install dependencies
npm install

# Build and deploy
npm run build
./deploy.sh deploy
```

### Testing

```bash
# Test the deployment
./deploy.sh test

# View logs
./deploy.sh logs
```

## 🔧 Configuration

### Environment Variables

- `CDK_DEFAULT_ACCOUNT`: AWS account ID (auto-detected)
- `CDK_DEFAULT_REGION`: AWS region (defaults to eu-central-1)

### Stack Configuration

Key configuration options in `lib/elb-tracking-stack.ts`:

```typescript
const functionName = 'event-processor';
const apiName = 'event-processor-api';
const redshiftSecretName = 'redshift-credentials';
const redshiftDatabase = 'dev';
const lambdaTimeout = cdk.Duration.seconds(30);
const lambdaMemorySize = 256;
const domainName = 'mnb.yourdomain.com'; // Replace with your actual domain
const hostedZoneId = 'Z04627343E8DYMW1I6O6C'; // Replace with your hosted zone ID
```

**Domain Configuration:**
- Update `domainName` with your subdomain (e.g., `mnb.yourdomain.com`)
- Update `hostedZoneId` with your Route 53 hosted zone ID
- The stack will automatically create the necessary DNS records and API Gateway custom domain

## 📊 Monitoring

### CloudWatch Alarms

- **Lambda Errors**: Triggers on function errors
- **Lambda Duration**: Triggers when execution time approaches timeout
- **API Gateway Errors**: Triggers on API Gateway errors

### Logs

- **Lambda Logs**: `/aws/lambda/{function-name}`
- **API Gateway Logs**: Detailed request/response logging

## 🔐 Security

### IAM Permissions

Lambda execution role includes:
- Basic Lambda execution (CloudWatch Logs)
- VPC access (ENI management)
- Secrets Manager read access
- Redshift connectivity

### Network Security

- **VPC**: Lambda runs in private subnets with NAT Gateway
- **Security Groups**: Isolated access between Lambda and Redshift
- **Redshift Serverless**: Private subnets with enhanced VPC routing
- **Secrets Manager**: Encrypted credential storage

## 📝 API Reference

### Endpoint

- **URL**: `https://{your-domain}/events` (e.g., `https://mnb.yourdomain.com/events`)
- **Method**: POST
- **Content-Type**: application/json
- **Custom Domain**: The stack creates a custom domain with SSL certificate
- to be used as a destination for elbwalker


### Response Format

#### Success (200)
```json
{
  "message": "Event processed successfully",
  "event_id": "string"
}
```

#### Error (400/500)
```json
{
  "error": "Error message"
}
```

## 🧪 Testing

### Manual Testing

```bash
# Get Custom Domain URL
CUSTOM_DOMAIN=$(aws cloudformation describe-stacks \
  --stack-name ElbTrackingStack \
  --query "Stacks[0].Outputs[?OutputKey=='CustomDomainName'].OutputValue" \
  --output text)

# Test with curl using custom domain
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "event": "test_event",
    "timestamp": 1703123456789,
    "id": "test-123",
    "data": {
      "id": "data-123",
      "device": "desktop",
      "source": "web"
    }
  }' \
  "https://$CUSTOM_DOMAIN/events"
```

### Automated Testing

```bash
./deploy.sh test
```

## 🛠️ Development

### Local Development

```bash
# Install dependencies
npm install

# Build the project
npm run build

# Synthesize CloudFormation template
npx cdk synth

# Diff with deployed stack
npx cdk diff

# Deploy changes
npx cdk deploy
```

### Lambda Function Development

1. Edit `lambda/lambda_function.py`
2. Update dependencies in `lambda/requirements.txt` if needed
3. Deploy using `./deploy.sh deploy`

## 🗑️ Cleanup

### Destroy the Stack

```bash
# Destroy all resources
./deploy.sh destroy

# Or use CDK directly
npx cdk destroy
```

## 🔍 Troubleshooting

### Debugging

#### View Stack Events
```bash
aws cloudformation describe-stack-events --stack-name ElbTrackingStack
```

#### View Lambda Logs
```bash
./deploy.sh logs
```

#### Test API Gateway
```bash
./deploy.sh test
```

## 📄 License

This project is licensed under the MIT License. 




