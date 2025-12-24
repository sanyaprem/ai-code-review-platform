import json
import os
import boto3
import ast
from typing import Dict, List, Any

s3_client = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'code-review-storage-sanya-2025')

def lambda_handler(event, context):
    """Parse Python code files using AST"""
    
    print("=" * 60)
    print("🔍 CODE PARSER Started (AST Analysis)")
    print("=" * 60)
    
    try:
        uploaded_files = event.get('uploaded_files', [])
        
        if not uploaded_files:
            return {
                "statusCode": 400,
                "error": "No uploaded_files provided"
            }
        
        print(f"📁 Parsing {len(uploaded_files)} files")
        
        parsed_files = []
        skipped_files = []
        total_functions = 0
        total_classes = 0
        total_lines = 0
        
        for file_info in uploaded_files:
            filename = file_info.get('filename', 'unknown')
            s3_key = file_info.get('s3_key')
            
            print(f"📄 Parsing: {filename}")
            
            try:
                # Download file from S3
                response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
                code = response['Body'].read().decode('utf-8')
                
                # Parse with AST
                parsed_data = parse_python_file(code, filename)
                
                if parsed_data:
                    parsed_files.append(parsed_data)
                    total_functions += parsed_data['metrics']['function_count']
                    total_classes += parsed_data['metrics']['class_count']
                    total_lines += parsed_data['metrics']['lines_of_code']
                    print(f"✅ Parsed {filename}: {parsed_data['metrics']['function_count']} functions, {parsed_data['metrics']['class_count']} classes")
                else:
                    skipped_files.append({
                        "filename": filename,
                        "reason": "Parse failed"
                    })
                    
            except Exception as e:
                print(f"❌ Error parsing {filename}: {str(e)}")
                skipped_files.append({
                    "filename": filename,
                    "reason": str(e)
                })
        
        statistics = {
            "total_files": len(uploaded_files),
            "parsed_files": len(parsed_files),
            "skipped_files": len(skipped_files),
            "total_functions": total_functions,
            "total_classes": total_classes,
            "total_lines": total_lines
        }
        
        print("=" * 60)
        print(f"✅ Code Parser Complete")
        print(f"📊 Parsed: {len(parsed_files)}/{len(uploaded_files)} files")
        print(f"   Functions: {total_functions}")
        print(f"   Classes: {total_classes}")
        print(f"   Lines: {total_lines}")
        print("=" * 60)
        
        return {
            "statusCode": 200,
            "parsed_files": parsed_files,
            "skipped_files": skipped_files,
            "statistics": statistics
        }
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR in CodeParser: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        return {
            "statusCode": 500,
            "error": str(e)
        }


def parse_python_file(code: str, filename: str) -> Dict[str, Any]:
    """Parse Python code using AST"""
    try:
        tree = ast.parse(code)
        
        functions = []
        classes = []
        imports = []
        
        # Extract top-level elements
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    "name": node.name,
                    "line": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "has_docstring": ast.get_docstring(node) is not None,
                    "decorators": [d.id if isinstance(d, ast.Name) else 'decorator' for d in node.decorator_list]
                }
                functions.append(func_info)
                
            elif isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                class_info = {
                    "name": node.name,
                    "line": node.lineno,
                    "methods": methods,
                    "bases": [b.id if isinstance(b, ast.Name) else 'base' for b in node.bases],
                    "has_docstring": ast.get_docstring(node) is not None
                }
                classes.append(class_info)
                
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "module": alias.name,
                        "alias": alias.asname,
                        "type": "import"
                    })
                    
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ""
                for alias in node.names:
                    imports.append({
                        "module": f"{module}.{alias.name}" if module else alias.name,
                        "alias": alias.asname,
                        "type": "from_import"
                    })
        
        # Calculate metrics
        lines = code.split('\n')
        lines_of_code = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        
        # Calculate complexity (simplified cyclomatic complexity)
        complexity = calculate_complexity(tree)
        
        # Documentation ratio
        documented_functions = sum(1 for f in functions if f['has_docstring'])
        documented_classes = sum(1 for c in classes if c['has_docstring'])
        total_documentable = len(functions) + len(classes)
        documentation_ratio = (documented_functions + documented_classes) / total_documentable if total_documentable > 0 else 1.0
        
        return {
            "filename": filename,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "metrics": {
                "lines_of_code": lines_of_code,
                "function_count": len(functions),
                "class_count": len(classes),
                "import_count": len(imports),
                "complexity": complexity,
                "documentation_ratio": documentation_ratio
            }
        }
        
    except SyntaxError as e:
        print(f"❌ Syntax error in {filename}: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Error parsing {filename}: {str(e)}")
        return None


def calculate_complexity(tree: ast.AST) -> int:
    """Calculate cyclomatic complexity"""
    complexity = 1  # Base complexity
    
    for node in ast.walk(tree):
        # Decision points increase complexity
        if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            complexity += len(node.values) - 1
        elif isinstance(node, (ast.And, ast.Or)):
            complexity += 1
    
    return complexity
