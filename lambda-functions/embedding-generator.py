import json
import boto3
import os
import uuid
from datetime import datetime
from decimal import Decimal
import google.generativeai as genai

# Initialize
dynamodb = boto3.resource('dynamodb')
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

EMBEDDINGS_TABLE = os.environ.get('EMBEDDINGS_TABLE', 'code_embeddings')

embeddings_table = dynamodb.Table(EMBEDDINGS_TABLE)


def generate_embedding(text):
    """Generate embedding vector for text using Gemini"""
    try:
        print(f"🔢 Generating embedding for {len(text)} characters")
        
        # Truncate if too long
        if len(text) > 8000:
            text = text[:8000]
            print(f"⚠️  Truncated to 8000 characters")
        
        # Gemini embeddings
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        
        embedding = result['embedding']
        print(f"✅ Generated {len(embedding)}-dimensional embedding")
        
        return embedding
        
    except Exception as e:
        print(f"❌ Embedding error: {str(e)}")
        return None


def extract_code_snippets(parsed_file, max_snippets=10):
    """Extract important code snippets for embedding"""
    snippets = []
    
    filename = parsed_file.get('filename', 'unknown')
    
    # Extract functions
    functions = parsed_file.get('functions', [])
    for func in functions[:max_snippets]:
        snippet = {
            'type': 'function',
            'name': func.get('name'),
            'filename': filename,
            'line': func.get('line'),
            'context': f"Function: {func.get('name')} with args {func.get('args', [])}"
        }
        snippets.append(snippet)
    
    # Extract classes
    classes = parsed_file.get('classes', [])
    for cls in classes[:max_snippets]:
        snippet = {
            'type': 'class',
            'name': cls.get('name'),
            'filename': filename,
            'line': cls.get('line'),
            'context': f"Class: {cls.get('name')} with methods {cls.get('methods', [])}"
        }
        snippets.append(snippet)
    
    return snippets


def store_embedding(embedding_data):
    """Store embedding in DynamoDB"""
    try:
        embedding_vector = [Decimal(str(float(x))) for x in embedding_data['embedding']]
        
        item = {
            'embedding_id': embedding_data['embedding_id'],
            'timestamp': embedding_data['timestamp'],
            'review_id': embedding_data.get('review_id'),
            'snippet_type': embedding_data['snippet_type'],
            'snippet_name': embedding_data['snippet_name'],
            'filename': embedding_data['filename'],
            'context': embedding_data['context'],
            'embedding_vector': embedding_vector,
            'embedding_dimension': len(embedding_vector),
            'vulnerability_type': embedding_data.get('vulnerability_type', 'none'),
            'performance_issue': embedding_data.get('performance_issue', False),
            'code_quality_issue': embedding_data.get('code_quality_issue', False)
        }
        
        embeddings_table.put_item(Item=item)
        print(f"✅ Stored embedding: {embedding_data['embedding_id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Storage error: {str(e)}")
        return False


def analyze_for_issues(agent_results):
    """Extract issues found by agents"""
    issues = {
        'vulnerabilities': [],
        'performance_issues': [],
        'quality_issues': []
    }
    
    security = agent_results.get('security', {})
    security_review = security.get('review', '').lower()
    
    if 'sql injection' in security_review:
        issues['vulnerabilities'].append('sql_injection')
    if 'hardcoded' in security_review and ('secret' in security_review or 'key' in security_review):
        issues['vulnerabilities'].append('hardcoded_secrets')
    if 'exec(' in security_review or 'eval(' in security_review:
        issues['vulnerabilities'].append('dangerous_eval')
    if 'xss' in security_review or 'cross-site scripting' in security_review:
        issues['vulnerabilities'].append('xss')
    if 'pickle' in security_review:
        issues['vulnerabilities'].append('unsafe_pickle')
    
    performance = agent_results.get('performance', {})
    performance_review = performance.get('review', '').lower()
    
    if 'o(n²)' in performance_review or 'nested loop' in performance_review:
        issues['performance_issues'].append('nested_loops')
    if 'n+1' in performance_review:
        issues['performance_issues'].append('n_plus_one_query')
    if 'memory leak' in performance_review:
        issues['performance_issues'].append('memory_leak')
    
    best_practices = agent_results.get('best_practices', {})
    quality_review = best_practices.get('review', '').lower()
    
    if 'missing docstring' in quality_review or 'no docstring' in quality_review:
        issues['quality_issues'].append('missing_documentation')
    if 'no type hint' in quality_review or 'missing type hint' in quality_review:
        issues['quality_issues'].append('missing_type_hints')
    if 'no error handling' in quality_review:
        issues['quality_issues'].append('missing_error_handling')
    
    return issues


def lambda_handler(event, context):
    """Generate and store embeddings for analyzed code"""
    
    print("=" * 60)
    print("🔢 EMBEDDING GENERATOR Started (Gemini)")
    print("=" * 60)
    
    try:
        review_id = event.get('review_id')
        parsed_files = event.get('parsed_files', [])
        agent_results = event.get('agent_results', {})
        
        if not review_id:
            return {
                'statusCode': 400,
                'error': 'No review_id provided'
            }
        
        print(f"📋 Review ID: {review_id}")
        print(f"📁 Parsed files: {len(parsed_files)}")
        
        issues = analyze_for_issues(agent_results)
        print(f"🔍 Found issues:")
        print(f"   - Vulnerabilities: {len(issues['vulnerabilities'])}")
        print(f"   - Performance: {len(issues['performance_issues'])}")
        print(f"   - Quality: {len(issues['quality_issues'])}")
        
        embeddings_created = 0
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        for parsed_file in parsed_files:
            snippets = extract_code_snippets(parsed_file)
            
            print(f"\n📄 Processing {parsed_file.get('filename')}: {len(snippets)} snippets")
            
            for snippet in snippets:
                embedding_vector = generate_embedding(snippet['context'])
                
                if embedding_vector:
                    embedding_id = f"emb_{uuid.uuid4().hex[:16]}"
                    
                    snippet_name = snippet.get('name', '').lower()
                    vulnerability_type = 'none'
                    performance_issue = False
                    quality_issue = False
                    
                    if 'query' in snippet_name and 'sql_injection' in issues['vulnerabilities']:
                        vulnerability_type = 'sql_injection'
                    elif 'search' in snippet_name and 'nested_loops' in issues['performance_issues']:
                        performance_issue = True
                    
                    if 'missing_documentation' in issues['quality_issues']:
                        quality_issue = True
                    
                    embedding_data = {
                        'embedding_id': embedding_id,
                        'timestamp': timestamp,
                        'review_id': review_id,
                        'snippet_type': snippet['type'],
                        'snippet_name': snippet['name'],
                        'filename': snippet['filename'],
                        'context': snippet['context'],
                        'embedding': embedding_vector,
                        'vulnerability_type': vulnerability_type,
                        'performance_issue': performance_issue,
                        'code_quality_issue': quality_issue
                    }
                    
                    if store_embedding(embedding_data):
                        embeddings_created += 1
        
        print("\n" + "=" * 60)
        print(f"✅ Embedding Generation Complete")
        print(f"📊 Embeddings created: {embeddings_created}")
        print(f"🤖 Using Gemini embeddings (FREE!)")
        print("=" * 60)
        
        return {
            'statusCode': 200,
            'review_id': review_id,
            'embeddings_created': embeddings_created,
            'embedding_mode': 'gemini',
            'issues_tracked': {
                'vulnerabilities': len(issues['vulnerabilities']),
                'performance': len(issues['performance_issues']),
                'quality': len(issues['quality_issues'])
            }
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        return {
            'statusCode': 500,
            'error': str(e)
        }