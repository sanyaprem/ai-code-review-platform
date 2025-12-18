# 🏗️ Architecture Documentation

## System Overview

The AI Code Review Platform uses a serverless, event-driven architecture on AWS, orchestrated by Step Functions and powered by Google Gemini 2.5 Flash API.

## High-Level Flow
```
GitHub PR → Webhook → API Gateway → Lambda → Step Functions
    ↓
Download Code → Parse → Enhance Context
    ↓
3 AI Agents (Parallel Analysis)
    ├── Security Agent
    ├── Performance Agent
    └── Best Practices Agent
    ↓
Aggregate Reviews → Post Comment → Generate Embeddings
```

## Components

### 1. GitHub Webhook
- **Trigger**: PR events (opened, synchronize, reopened)
- **Security**: HMAC-SHA256 signature verification

### 2. API Gateway
- **Type**: REST API
- **Endpoint**: `/webhook` (POST)
- **Integration**: AWS Lambda (Proxy)

### 3. Lambda Functions

**GithubWebhookHandler**
- Verifies webhook signature
- Extracts PR metadata
- Starts Step Functions

**CodeDownloader**
- Fetches changed files from GitHub
- Uploads to S3

**CodeParser**
- AST-based parsing
- Extracts functions, classes, complexity

**ContextEnhancer**
- Identifies patterns
- Security, performance, quality signals

**AI Agents (3x)**
- SecurityAgent: Vulnerabilities, OWASP Top 10
- PerformanceAgent: Big-O analysis, optimization
- BestPracticesAgent: Code quality, PEP 8

**ReviewAggregator**
- Combines all reviews
- Formats markdown output

**GitHubCommentPoster**
- Posts review to PR

**EmbeddingGenerator**
- Generates vectors for RAG

### 4. Storage

**S3**
- Code files
- Embeddings
- Encryption: SSE-S3

**DynamoDB**
- Review metadata
- History
- Encryption: KMS

**Secrets Manager**
- API keys
- Tokens
- 5-minute TTL cache

### 5. Monitoring

**CloudWatch**
- Dashboard (11 widgets)
- 4 Alarms
- Logs retention: 30 days

**SNS**
- Email notifications
- Error alerts

## Performance Metrics

- **Cold Start**: 2,153ms
- **Execution**: 12-19 seconds
- **Package Size**: 26.64 MB
- **Cost**: $0.00 per review

## Security

- HMAC-SHA256 webhook verification
- IAM least-privilege policies
- Encryption at rest and in transit
- Secret rotation support

---

**Last Updated**: December 18, 2025
**Version**: 1.0.0
