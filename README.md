# 🤖 AI Code Review Platform

[![AWS](https://img.shields.io/badge/AWS-Serverless-orange?logo=amazon-aws)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini%202.5%20Flash-blue?logo=google)](https://deepmind.google/technologies/gemini/)
[![Cost](https://img.shields.io/badge/Cost-$0.00-success)](https://github.com/sanyaprem/ai-code-review-platform)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**An intelligent, multi-agent AI system that automatically reviews pull requests with specialized security, performance, and best practices analysis—completely free using Google Gemini 2.5 Flash.**

---

## 🎯 **What Makes This Special?**

- **🔒 Multi-Agent Intelligence**: Three specialized AI agents (Security, Performance, Best Practices) analyze code in parallel
- **💰 100% Free**: Uses Google Gemini 2.5 Flash API (1.5M tokens/min, FREE tier)
- **⚡ Lightning Fast**: Optimized cold starts (~2.1s), efficient execution (~12-19s)
- **🔐 Enterprise Security**: HMAC-SHA256 webhook verification, AWS Secrets Manager, encrypted storage
- **📊 Production Ready**: CloudWatch monitoring, SNS alerts, comprehensive error handling
- **🚀 Serverless**: Auto-scaling, pay-per-use AWS Lambda architecture

---

## ✨ **Key Features**

### 🤖 **Intelligent Code Analysis**
- **AST-Based Parsing**: Extracts functions, classes, imports, and complexity metrics
- **Context Enhancement**: Identifies security, performance, and quality patterns
- **Parallel Execution**: Three AI agents analyze simultaneously for speed
- **Comprehensive Reviews**: Detailed findings with code examples and fixes

### 🔒 **Security-First Design**
- **Webhook Verification**: HMAC-SHA256 signature validation
- **Secrets Management**: AWS Secrets Manager with 5-minute TTL caching
- **Encryption**: S3 SSE-S3, DynamoDB KMS encryption at rest
- **Least Privilege IAM**: Granular permissions for every component

### ⚡ **Performance Optimized**
- **Package Size**: Reduced from 31.9 MB → 26.64 MB (-16.5%)
- **Cold Start**: Improved from 2,648ms → 2,153ms (-18.7%)
- **Execution Time**: Reduced by 40.4% through optimization
- **Smart Caching**: Connection pooling, secret caching, warm Lambda reuse

---

## 🏗️ **Architecture**
```
GitHub PR → Webhook → API Gateway → Lambda → Step Functions
    ↓
Download Code → Parse → Enhance Context → 3 AI Agents (Parallel)
    ↓
Aggregate Reviews → Post Comment → Generate Embeddings
```

**Total Time**: ~25-35 seconds per review

---

## 🚀 **Quick Start**

### Prerequisites

- AWS Account with CLI configured
- Python 3.11+
- GitHub account
- Google AI Studio API key (FREE)

### Installation

See [docs/setup-guide.md](docs/setup-guide.md) for detailed setup instructions.

---

## 💰 **Cost Analysis**

### Current Costs: **$0.00/month**

| Service | Cost |
|---------|------|
| **Google Gemini 2.5 Flash** | **FREE** |
| **AWS Lambda** | $0.00 (Free tier) |
| **S3** | $0.023 |
| **DynamoDB** | $0.00 (Free tier) |
| **Secrets Manager** | $1.20 |
| **Total** | **~$1.27/month** |

---

## 📊 **Performance Metrics**

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Package Size** | 31.9 MB | 26.64 MB | **-16.5%** |
| **Cold Start** | 2,648 ms | 2,153 ms | **-18.7%** |
| **Execution Time** | 21,428 ms | 12,762 ms | **-40.4%** |
| **Cost per Review** | $0.00 | $0.00 | **FREE** |

---

## 🛠️ **Tech Stack**

- **Cloud**: AWS Lambda, Step Functions, API Gateway, S3, DynamoDB
- **AI**: Google Gemini 2.5 Flash
- **Language**: Python 3.11
- **Security**: AWS Secrets Manager, HMAC-SHA256, KMS encryption

---

## 📖 **Documentation**

- [📘 Setup Guide](docs/setup-guide.md)
- [🏗️ Architecture](docs/architecture.md)
- [🤝 Contributing](CONTRIBUTING.md)

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📧 **Contact**

- **GitHub**: [@sanyaprem](https://github.com/sanyaprem)
- **LinkedIn**: [Sanya Prem](https://linkedin.com/in/yourprofile)

---

**Built with ❤️ by Sanya Prem**

[⬆ Back to Top](#-ai-code-review-platform)
