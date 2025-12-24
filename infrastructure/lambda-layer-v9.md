# Lambda Layer v9 - Build Instructions

## Layer Name
code-review-dependencies (version 9)

## ARN
rn:aws:lambda:ap-south-2:943598056428:layer:code-review-dependencies:9

## Runtime
Python 3.12

## Dependencies
- requests
- openai
- google-generativeai

## Build Instructions (Windows)

### Method 1: Using pip with platform flag (RECOMMENDED)
```powershell
# Create infrastructure directory
mkdir infrastructure
cd infrastructure

# Document Lambda Layer v9
@"
# Lambda Layer v9 - Build Instructions

## Layer Name
code-review-dependencies (version 9)

## ARN
rn:aws:lambda:ap-south-2:943598056428:layer:code-review-dependencies:9

## Runtime
Python 3.12

## Dependencies
- requests
- openai
- google-generativeai

## Build Instructions (Windows)

### Method 1: Using pip with platform flag (RECOMMENDED)
```powershell
# Create temporary directory
mkdir C:\Users\pbsan\AppData\Local\Temp\lambda-layer-v9
cd C:\Users\pbsan\AppData\Local\Temp\lambda-layer-v9

# Install dependencies for Linux
pip install 
  --platform manylinux2014_x86_64 
  --target ./python 
  --implementation cp 
  --python-version 3.12 
  --only-binary=:all: 
  --upgrade 
  requests openai google-generativeai

# Create ZIP
Compress-Archive -Path .\python -DestinationPath layer-v9.zip

# Upload to AWS
aws lambda publish-layer-version 
  --layer-name code-review-dependencies 
  --description "Dependencies for AI Code Review (requests, openai, google-ai)" 
  --zip-file fileb://layer-v9.zip 
  --compatible-runtimes python3.12 
  --region ap-south-2
```

### Method 2: Using AWS CloudShell (if Method 1 fails)
```bash
# In AWS CloudShell (Linux environment)
mkdir lambda-layer
cd lambda-layer
mkdir -p python/lib/python3.12/site-packages
pip install requests openai google-generativeai -t python/lib/python3.12/site-packages
zip -r layer.zip python
aws lambda publish-layer-version --layer-name code-review-dependencies --zip-file fileb://layer.zip --compatible-runtimes python3.12 --region ap-south-2
```

## Attach to Lambda Functions
```powershell
# Attach to EmbeddingGenerator
aws lambda update-function-configuration 
  --function-name EmbeddingGenerator 
  --layers arn:aws:lambda:ap-south-2:943598056428:layer:code-review-dependencies:9 
  --region ap-south-2

# Attach to all other functions
aws lambda update-function-configuration --function-name SecurityAgent --layers arn:aws:lambda:ap-south-2:943598056428:layer:code-review-dependencies:9 --region ap-south-2
aws lambda update-function-configuration --function-name PerformanceAgent --layers arn:aws:lambda:ap-south-2:943598056428:layer:code-review-dependencies:9 --region ap-south-2
aws lambda update-function-configuration --function-name BestPracticesAgent --layers arn:aws:lambda:ap-south-2:943598056428:layer:code-review-dependencies:9 --region ap-south-2
```

## Known Issues
- Windows-built layers without --platform flag cause invalid ELF header errors on Lambda
- Always use Linux-compatible binaries for Lambda deployment
