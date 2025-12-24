# Step Functions State Machine Definition

## State Machine Name
CodeReviewOrchestrator

## ARN
rn:aws:states:ap-south-2:943598056428:stateMachine:CodeReviewOrchestrator

## Workflow States

1. **DownloadCode** - Downloads changed files from GitHub PR
2. **ParseCode** - Parses Python files using AST
3. **EnhanceContext** - Adds historical context and risk scoring
4. **RunAgents (Parallel)** - Runs 3 AI agents simultaneously:
   - SecurityAgent
   - PerformanceAgent
   - BestPracticesAgent
5. **AggregateResults** - Combines all agent reviews + saves to DynamoDB
6. **PostComment** - Posts review comment to GitHub PR
7. **GenerateEmbeddings** - Creates vector embeddings for RAG (optional)

## State Machine Definition
See step-function-definition.json for the complete ASL definition.

## Deployment
```powershell
aws stepfunctions create-state-machine 
  --name CodeReviewOrchestrator 
  --role-arn arn:aws:iam::943598056428:role/StepFunctionsExecutionRole 
  --definition file://step-function-definition.json 
  --region ap-south-2
```
