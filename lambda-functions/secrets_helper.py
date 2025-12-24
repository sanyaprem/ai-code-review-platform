"""
Secrets Manager helper with optimized caching
"""

import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

# Initialize client OUTSIDE handler for connection reuse
secrets_client = boto3.client('secretsmanager', region_name='ap-south-2')

# Cache with expiration
_secrets_cache = {}
_cache_expiry = {}
CACHE_TTL_SECONDS = 300  # 5 minutes

def get_secret(secret_name: str, force_refresh: bool = False) -> dict:
    """
    Retrieve secret from AWS Secrets Manager with TTL-based caching
    
    Args:
        secret_name: Name of the secret
        force_refresh: Bypass cache
    
    Returns:
        Dictionary containing secret key-value pairs
    """
    
    current_time = datetime.now()
    
    # Check cache validity
    if not force_refresh and secret_name in _secrets_cache:
        if secret_name in _cache_expiry and current_time < _cache_expiry[secret_name]:
            print(json.dumps({
                "level": "INFO",
                "message": f"Using cached secret: {secret_name}",
                "cache_hit": True
            }))
            return _secrets_cache[secret_name]
    
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        
        if 'SecretString' in response:
            secret_dict = json.loads(response['SecretString'])
        else:
            import base64
            secret_dict = json.loads(base64.b64decode(response['SecretBinary']))
        
        # Update cache with expiration
        _secrets_cache[secret_name] = secret_dict
        _cache_expiry[secret_name] = current_time + timedelta(seconds=CACHE_TTL_SECONDS)
        
        print(json.dumps({
            "level": "INFO",
            "message": f"Successfully retrieved and cached secret: {secret_name}",
            "cache_hit": False
        }))
        
        return secret_dict
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        print(json.dumps({
            "level": "ERROR",
            "message": f"Failed to retrieve secret: {secret_name}",
            "error_code": error_code
        }))
        
        if error_code == 'ResourceNotFoundException':
            raise Exception(f"Secret not found: {secret_name}")
        elif error_code == 'AccessDeniedException':
            raise Exception(f"Access denied to secret: {secret_name}")
        else:
            raise Exception(f"Error retrieving secret: {secret_name}")
    
    except Exception as e:
        print(json.dumps({
            "level": "ERROR",
            "message": f"Unexpected error retrieving secret: {secret_name}",
            "error": str(e)
        }))
        raise

def get_gemini_api_key() -> str:
    """Get Gemini API key from Secrets Manager with caching"""
    secrets = get_secret('CodeReview/GeminiAPIKey')
    return secrets.get('GEMINI_API_KEY')