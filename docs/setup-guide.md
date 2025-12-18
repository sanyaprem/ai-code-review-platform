# 📘 Setup Guide

## Prerequisites

- AWS Account with CLI configured
- Python 3.11+
- GitHub account
- Google AI Studio API key (FREE)

## Step 1: AWS Setup

### Create S3 Bucket
```bash
aws s3 mb s3://code-review-storage-YOUR-NAME-2025 --region ap-south-2
```

### Create DynamoDB Table
```bash
aws dynamodb create-table \
  --table-name CodeReviews \
  --attribute-definitions AttributeName=review_id,AttributeType=S \
  --key-schema AttributeName=review_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region ap-south-2
```

### Create Secrets
```bash
# Gemini API Key
aws secretsmanager create-secret \
  --name CodeReview/GeminiAPIKey \
  --secret-string '{"GEMINI_API_KEY":"your-key"}' \
  --region ap-south-2

# GitHub Webhook Secret
aws secretsmanager create-secret \
  --name CodeReview/GitHubWebhookSecret \
  --secret-string '{"GITHUB_WEBHOOK_SECRET":"your-secret"}' \
  --region ap-south-2

# GitHub Token
aws secretsmanager create-secret \
  --name CodeReview/GitHubToken \
  --secret-string '{"GITHUB_TOKEN":"ghp_your-token"}' \
  --region ap-south-2
```

## Step 2: Deploy Lambda Functions

See deployment scripts in `scripts/` directory.

## Step 3: Configure GitHub Webhook

1. Go to repository Settings → Webhooks
2. Add webhook:
   - **URL**: Your API Gateway endpoint
   - **Content type**: application/json
   - **Secret**: Your webhook secret
   - **Events**: Pull requests

## Step 4: Test

Create a test PR and watch the AI review it!

---

For detailed instructions, see the main README.
