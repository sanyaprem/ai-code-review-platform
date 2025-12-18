import json
import hmac
import hashlib
import boto3
from datetime import datetime

# Initialize clients
secretsmanager = boto3.client('secretsmanager', region_name='ap-south-2')
stepfunctions = boto3.client('stepfunctions', region_name='ap-south-2')

# Cache for webhook secret
_webhook_secret = None

def get_webhook_secret():
    """Get GitHub webhook secret from Secrets Manager with caching"""
    global _webhook_secret
    
    if _webhook_secret:
        return _webhook_secret
    
    try:
        response = secretsmanager.get_secret_value(SecretId='CodeReview/GitHubWebhookSecret')
        secret_dict = json.loads(response['SecretString'])
        _webhook_secret = secret_dict.get('GITHUB_WEBHOOK_SECRET')
        print(f"✅ Retrieved webhook secret from Secrets Manager")
        return _webhook_secret
    except Exception as e:
        print(f"❌ Error retrieving webhook secret: {str(e)}")
        raise

def verify_signature(payload_body, signature_header):
    """Verify GitHub webhook signature"""
    if not signature_header:
        return False
    
    secret = get_webhook_secret()
    if not secret:
        return False
    
    # GitHub sends signature as 'sha256=...'
    expected_signature = 'sha256=' + hmac.new(
        secret.encode('utf-8'),
        payload_body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Constant-time comparison
    return hmac.compare_digest(expected_signature, signature_header)

def lambda_handler(event, context):
    """Handle GitHub webhook events"""
    
    print("=" * 60)
    print("🪝 GITHUB WEBHOOK HANDLER")
    print("=" * 60)
    
    try:
        # Get signature from headers
        headers = event.get('headers', {})
        signature = headers.get('x-hub-signature-256') or headers.get('X-Hub-Signature-256')
        
        # Get raw body
        body = event.get('body', '')
        
        # Verify signature
        if not verify_signature(body, signature):
            print("❌ Invalid webhook signature")
            return {
                'statusCode': 401,
                'body': json.dumps({
                    'error': 'Invalid signature',
                    'message': 'Webhook signature verification failed'
                })
            }
        
        print("✅ Webhook signature verified")
        
        # Parse payload
        payload = json.loads(body)
        
        # Get event type
        event_type = headers.get('x-github-event') or headers.get('X-GitHub-Event')
        
        print(f"📋 Event type: {event_type}")
        
        # Handle ping event
        if event_type == 'ping':
            print("🏓 Ping event received")
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Pong! Webhook configured successfully'})
            }
        
        # Handle pull request events
        if event_type == 'pull_request':
            action = payload.get('action')
            pr_number = payload['pull_request']['number']
            repo_name = payload['repository']['full_name']
            
            print(f"🔀 PR #{pr_number} - Action: {action}")
            print(f"📦 Repository: {repo_name}")
            
            # Only process opened, synchronize, or reopened PRs
            if action not in ['opened', 'synchronize', 'reopened']:
                print(f"⏭️  Skipping action: {action}")
                return {
                    'statusCode': 200,
                    'body': json.dumps({'message': f'Skipped action: {action}'})
                }
            
            # Start Step Functions workflow
            state_machine_arn = 'arn:aws:states:ap-south-2:943598056428:stateMachine:CodeReviewOrchestrator'
            
            execution_input = {
                'pr_number': pr_number,
                'repo_name': repo_name,
                'action': action,
                'payload': payload
            }
            
            response = stepfunctions.start_execution(
                stateMachineArn=state_machine_arn,
                name=f"pr-{pr_number}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                input=json.dumps(execution_input)
            )
            
            print(f"🚀 Started Step Functions execution: {response['executionArn']}")
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Code review started',
                    'pr_number': pr_number,
                    'execution_arn': response['executionArn']
                })
            }
        
        # Unknown event type
        print(f"⚠️  Unknown event type: {event_type}")
        return {
            'statusCode': 200,
            'body': json.dumps({'message': f'Received {event_type} event'})
        }
        
    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal error',
                'message': str(e)
            })
        }