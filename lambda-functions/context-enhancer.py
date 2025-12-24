import json
import os
import boto3
from typing import Dict, List, Any
from decimal import Decimal

# Initialize clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

EMBEDDINGS_TABLE = os.environ.get('EMBEDDINGS_TABLE', 'code_embeddings')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'code-review-storage-sanya-2025')

def lambda_handler(event, context):
    """Enhance code analysis with historical context from RAG pipeline"""
    
    print("=" * 60)
    print("🧠 CONTEXT ENHANCER Started (RAG Pipeline)")
    print("=" * 60)
    
    try:
        parsed_files = event.get('parsed_files', [])
        
        if not parsed_files:
            return {
                "statusCode": 400,
                "error": "No parsed_files provided"
            }
        
        print(f"📁 Enhancing context for {len(parsed_files)} files")
        
        context_map = {}
        total_patterns = 0
        security_patterns = 0
        performance_patterns = 0
        quality_patterns = 0
        
        for parsed_file in parsed_files:
            filename = parsed_file.get('filename', 'unknown')
            
            print(f"📄 Analyzing: {filename}")
            
            # Identify patterns in the code
            patterns = identify_code_patterns(parsed_file)
            
            # Try to find similar historical issues (simplified for now)
            historical_context = find_historical_context(parsed_file, patterns)
            
            context_map[filename] = {
                "patterns": patterns,
                "historical_issues": historical_context,
                "risk_score": calculate_risk_score(patterns)
            }
            
            total_patterns += len(patterns['security']) + len(patterns['performance']) + len(patterns['quality'])
            security_patterns += len(patterns['security'])
            performance_patterns += len(patterns['performance'])
            quality_patterns += len(patterns['quality'])
            
            print(f"✅ {filename}: {len(patterns['security'])} security, {len(patterns['performance'])} performance, {len(patterns['quality'])} quality patterns")
        
        statistics = {
            "total_files": len(parsed_files),
            "total_patterns": total_patterns,
            "security_patterns": security_patterns,
            "performance_patterns": performance_patterns,
            "quality_patterns": quality_patterns
        }
        
        print("=" * 60)
        print(f"✅ Context Enhancer Complete")
        print(f"📊 Patterns identified: {total_patterns}")
        print(f"   🔒 Security: {security_patterns}")
        print(f"   ⚡ Performance: {performance_patterns}")
        print(f"   📚 Quality: {quality_patterns}")
        print("=" * 60)
        
        return {
            "statusCode": 200,
            "context_map": context_map,
            "statistics": statistics
        }
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR in ContextEnhancer: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        return {
            "statusCode": 500,
            "error": str(e)
        }


def identify_code_patterns(parsed_file: Dict[str, Any]) -> Dict[str, List[str]]:
    """Identify security, performance, and quality patterns in code"""
    
    patterns = {
        "security": [],
        "performance": [],
        "quality": []
    }
    
    functions = parsed_file.get('functions', [])
    classes = parsed_file.get('classes', [])
    imports = parsed_file.get('imports', [])
    metrics = parsed_file.get('metrics', {})
    
    # Security patterns
    import_modules = [imp['module'] for imp in imports]
    
    if any('sql' in mod.lower() for mod in import_modules):
        patterns['security'].append('sql_operations')
    
    if any(mod in ['pickle', 'subprocess', 'eval'] for mod in import_modules):
        patterns['security'].append('dangerous_imports')
    
    if any('request' in mod.lower() or 'http' in mod.lower() for mod in import_modules):
        patterns['security'].append('http_operations')
    
    for func in functions:
        func_name = func.get('name', '').lower()
        
        if any(keyword in func_name for keyword in ['auth', 'login', 'password', 'token']):
            patterns['security'].append('authentication_function')
        
        if 'query' in func_name or 'sql' in func_name:
            patterns['security'].append('database_query')
        
        if 'validate' in func_name or 'sanitize' in func_name:
            patterns['security'].append('input_validation')
    
    # Performance patterns
    complexity = metrics.get('complexity', 0)
    if complexity > 10:
        patterns['performance'].append('high_complexity')
    
    for func in functions:
        func_name = func.get('name', '').lower()
        
        if 'loop' in func_name or 'iterate' in func_name:
            patterns['performance'].append('iteration_function')
        
        if 'search' in func_name or 'find' in func_name:
            patterns['performance'].append('search_operation')
        
        if 'sort' in func_name or 'order' in func_name:
            patterns['performance'].append('sorting_operation')
    
    # Quality patterns
    doc_ratio = metrics.get('documentation_ratio', 0)
    if doc_ratio < 0.5:
        patterns['quality'].append('low_documentation')
    
    if metrics.get('function_count', 0) > 20:
        patterns['quality'].append('large_file')
    
    for func in functions:
        if not func.get('has_docstring'):
            patterns['quality'].append('missing_docstring')
            break  # Only add once
    
    for cls in classes:
        if not cls.get('has_docstring'):
            patterns['quality'].append('missing_class_docstring')
            break  # Only add once
    
    return patterns


def find_historical_context(parsed_file: Dict[str, Any], patterns: Dict[str, List[str]]) -> List[Dict[str, str]]:
    """Find similar historical issues from past reviews (simplified version)"""
    
    # This is a simplified version. In production, you'd query the embeddings table
    # and use vector similarity search to find related past issues.
    
    historical_issues = []
    
    # Security context
    if 'sql_operations' in patterns['security']:
        historical_issues.append({
            "category": "security",
            "issue": "SQL operations detected - check for SQL injection vulnerabilities",
            "severity": "high",
            "recommendation": "Use parameterized queries or ORM"
        })
    
    if 'dangerous_imports' in patterns['security']:
        historical_issues.append({
            "category": "security",
            "issue": "Dangerous imports detected (pickle, subprocess, eval)",
            "severity": "critical",
            "recommendation": "Review usage and implement proper input validation"
        })
    
    if 'authentication_function' in patterns['security']:
        historical_issues.append({
            "category": "security",
            "issue": "Authentication/authorization code detected",
            "severity": "high",
            "recommendation": "Ensure proper password hashing, token management, and session security"
        })
    
    # Performance context
    if 'high_complexity' in patterns['performance']:
        historical_issues.append({
            "category": "performance",
            "issue": "High cyclomatic complexity detected",
            "severity": "medium",
            "recommendation": "Consider refactoring into smaller functions"
        })
    
    if 'search_operation' in patterns['performance']:
        historical_issues.append({
            "category": "performance",
            "issue": "Search operation detected",
            "severity": "medium",
            "recommendation": "Ensure efficient algorithm (avoid O(n²) nested loops)"
        })
    
    # Quality context
    if 'low_documentation' in patterns['quality']:
        historical_issues.append({
            "category": "quality",
            "issue": "Low documentation coverage",
            "severity": "low",
            "recommendation": "Add docstrings to functions and classes"
        })
    
    if 'large_file' in patterns['quality']:
        historical_issues.append({
            "category": "quality",
            "issue": "Large file with many functions",
            "severity": "low",
            "recommendation": "Consider splitting into multiple modules"
        })
    
    return historical_issues


def calculate_risk_score(patterns: Dict[str, List[str]]) -> float:
    """Calculate overall risk score based on patterns"""
    
    # Weight different pattern categories
    security_weight = 5.0
    performance_weight = 2.0
    quality_weight = 1.0
    
    security_score = len(patterns['security']) * security_weight
    performance_score = len(patterns['performance']) * performance_weight
    quality_score = len(patterns['quality']) * quality_weight
    
    total_score = security_score + performance_score + quality_score
    
    # Normalize to 0-10 scale
    max_possible = 50  # Arbitrary max for normalization
    normalized_score = min(total_score / max_possible * 10, 10.0)
    
    return round(normalized_score, 2)
