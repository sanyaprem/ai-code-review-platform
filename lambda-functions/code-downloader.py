import json
import boto3
import urllib3
from datetime import datetime

s3_client = boto3.client('s3')
http = urllib3.PoolManager()

BUCKET_NAME = 'code-review-storage-sanya-2025'

def lambda_handler(event, context):
    """Download changed files from GitHub PR"""
    
    print("=" * 60)
    print("📥 CODE DOWNLOADER (GitHub Integration)")
    print("=" * 60)
    
    try:
        # Extract PR information
        pr_number = event.get('pr_number')
        repo_name = event.get('repo_name')
        payload = event.get('payload', {})
        
        if not all([pr_number, repo_name, payload]):
            return {
                "statusCode": 400,
                "error": "Missing required parameters: pr_number, repo_name, or payload"
            }
        
        print(f"📋 PR #{pr_number} from {repo_name}")
        
        # Get PR files from GitHub API
        pull_request = payload.get('pull_request', {})
        pr_url = pull_request.get('url')
        
        if not pr_url:
            return {
                "statusCode": 400,
                "error": "Invalid payload: missing pull_request.url"
            }
        
        # Get list of changed files
        files_url = f"{pr_url}/files"
        
        print(f"🔍 Fetching changed files from: {files_url}")
        
        response = http.request('GET', files_url, headers={
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'AI-Code-Review-Platform'
        })
        
        if response.status != 200:
            return {
                "statusCode": response.status,
                "error": f"Failed to fetch PR files: {response.status}"
            }
        
        files = json.loads(response.data.decode('utf-8'))
        
        print(f"📁 Found {len(files)} changed files")
        
        # Download and upload Python files
        uploaded_files = []
        
        for file_info in files:
            filename = file_info.get('filename', '')
            raw_url = file_info.get('raw_url')
            status = file_info.get('status')  # added, modified, removed
            
            # Skip non-Python files and removed files
            if not filename.endswith('.py') or status == 'removed':
                print(f"⏭️  Skipping: {filename} (status: {status})")
                continue
            
            print(f"📄 Downloading: {filename}")
            
            # Download file content
            file_response = http.request('GET', raw_url)
            
            if file_response.status != 200:
                print(f"❌ Failed to download {filename}")
                continue
            
            file_content = file_response.data.decode('utf-8')
            
            # Upload to S3
            s3_key = f"repos/{repo_name}/pr-{pr_number}/{filename}"
            
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_key,
                Body=file_content.encode('utf-8'),
                ContentType='text/plain'
            )
            
            uploaded_files.append({
                "filename": filename,
                "s3_key": s3_key,
                "size": len(file_content)
            })
            
            print(f"✅ Uploaded to S3: {s3_key}")
        
        print("=" * 60)
        print(f"✅ Downloaded {len(uploaded_files)} Python files")
        print("=" * 60)
        
        return {
            "statusCode": 200,
            "uploaded_files": uploaded_files,
            "total_files": len(files),
            "python_files": len(uploaded_files)
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        return {
            "statusCode": 500,
            "error": str(e)
        }