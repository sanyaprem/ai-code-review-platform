import json
import os
import boto3
import google.generativeai as genai
from secrets_helper import get_gemini_api_key

s3_client = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'code-review-storage-sanya-2025')

def lambda_handler(event, context):
    """Best practices code review agent powered by Gemini"""
    
    lambda_name = "BestPracticesAgent"
    
    try:
        print("=" * 60)
        print("📚 BEST PRACTICES AGENT Started (Gemini AI)")
        print("=" * 60)
        
        if 'uploaded_files' not in event:
            return {
                "statusCode": 400,
                "error": True,
                "message": "Missing required field: uploaded_files",
                "lambda": lambda_name
            }
        
        uploaded_files = event.get('uploaded_files', [])
        parsed_files = event.get('parsed_files', [])
        
        print(f"📁 Analyzing {len(uploaded_files)} files for code quality")
        
        # Configure Gemini with Secrets Manager
        try:
            api_key = get_gemini_api_key()
            if not api_key:
                return {
                    "statusCode": 500,
                    "error": True,
                    "message": "GEMINI_API_KEY not found in Secrets Manager",
                    "lambda": lambda_name
                }
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            print("✅ Gemini API key retrieved from Secrets Manager")
            
        except Exception as e:
            print(f"❌ Error retrieving API key: {str(e)}")
            return {
                "statusCode": 500,
                "error": True,
                "message": f"Failed to retrieve API key from Secrets Manager: {str(e)}",
                "lambda": lambda_name
            }
        
        all_reviews = []
        total_tokens = 0
        
        for file_info in uploaded_files:
            filename = file_info.get('filename', 'unknown')
            s3_key = file_info.get('s3_key')
            
            print(f"📄 Processing: {filename}")
            
            try:
                response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
                code = response['Body'].read().decode('utf-8')
            except Exception as e:
                print(f"❌ Error downloading {s3_key}: {str(e)}")
                all_reviews.append({
                    "file": filename,
                    "review": f"Error: Could not download file - {str(e)}",
                    "tokens": 0
                })
                continue
            
            parsed_meta = next((p for p in parsed_files if p.get('filename') == filename), {})
            
            try:
                prompt = create_best_practices_prompt(code, filename, parsed_meta)
                response = model.generate_content(prompt)
                review_text = response.text
                tokens_used = len(prompt.split()) + len(review_text.split())
                
                all_reviews.append({
                    "file": filename,
                    "review": review_text,
                    "tokens": tokens_used
                })
                
                total_tokens += tokens_used
                
            except Exception as e:
                print(f"❌ Error analyzing {filename}: {str(e)}")
                all_reviews.append({
                    "file": filename,
                    "review": f"Error analyzing file: {str(e)}",
                    "tokens": 0
                })
        
        combined_review = "\n\n".join([f"## File: {r['file']}\n\n{r['review']}" for r in all_reviews])
        
        print("=" * 60)
        print("✅ Best Practices Agent Complete")
        print(f"📊 Total tokens: {total_tokens}")
        print(f"💰 Total cost: $0.0000 (FREE with Gemini!)")
        print("=" * 60)
        
        return {
            "statusCode": 200,
            "agent": "best_practices",
            "review": f"# 📚 BEST PRACTICES ANALYSIS\n\n{combined_review}",
            "tokens": total_tokens,
            "cost": 0.0
        }
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR in {lambda_name}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        return {
            "statusCode": 500,
            "error": True,
            "message": str(e),
            "lambda": lambda_name
        }

def create_best_practices_prompt(code, filename, parsed_meta):
    """Create best practices prompt"""
    context = ""
    if parsed_meta:
        metrics = parsed_meta.get('metrics', {})
        context = f"""
**File Metadata:**
- Functions: {metrics.get('function_count', 0)}
- Classes: {metrics.get('class_count', 0)}
- Documentation: {metrics.get('documentation_ratio', 0)*100:.0f}%
"""
    
    prompt = f"""You are a code quality expert reviewing Python code for best practices.

{context}

**Code to analyze:**
```python
{code}
```

**Your task:**
1. Check for PEP 8 compliance
2. Evaluate naming conventions
3. Check for missing docstrings and type hints
4. Identify code smells and maintainability issues
5. Suggest refactoring improvements

**Output format:**
## 📚 Code Quality Issues
[List issues with examples]

## 📝 Documentation Issues
[Missing docstrings, type hints, etc.]

## ♻️ Refactoring Suggestions
[Specific improvements with code examples]

## ✅ Best Practices Summary
[Overall assessment and prioritized recommendations]
"""
    return prompt