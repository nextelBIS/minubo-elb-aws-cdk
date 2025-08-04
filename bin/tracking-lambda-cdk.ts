#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { ElbTrackingStack } from '../lib/elb-tracking-stack';

const app = new cdk.App();

// Create the main stack
new ElbTrackingStack(app, 'ElbTrackingStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'eu-central-1',
  },
  description: 'Tracking Lambda with API Gateway and Redshift integration',
});

// Add tags to all resources
cdk.Tags.of(app).add('Project', 'tracking-lambda');
cdk.Tags.of(app).add('Environment', 'dev');
cdk.Tags.of(app).add('ManagedBy', 'CDK'); 