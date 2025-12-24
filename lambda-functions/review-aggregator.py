import json
import os
import boto3
import uuid
from datetime import datetime
from decimal import Decimal

# Initialize clients
dynamodb = boto3.resource('dynamodb')

REVIEWS_TABLE = os.environ.get('REVIEWS_TABLE', 'CodeReviews')
reviews_table = dynamodb.Table(REVIEWS_TABLE)

def lambda_handler(event, context):
    """Aggregate reviews from all agents into a single formatted report"""
    
    print("=" * 60)
    print("📊 REVIEW AGGREGATOR Started")
    print("=" * 60)
    
    try:
        # Get agent results
        security = event.get('security', {})
        performance = event.get('performance', {})
        best_practices = event.get('best_practices', {})
        
        # Get additional context
        parse_statistics = event.get('parse_statistics', {})
        context_statistics = event.get('context_statistics', {})
        repo_name = event.get('repo_name', 'unknown')
        pr_number = event.get('pr_number', 0)
        
        print(f"📋 Aggregating reviews for PR #{pr_number} in {repo_name}")
        
        # Check if agents returned errors
        security_error = security.get('error', False)
        performance_error = performance.get('error', False)
        best_practices_error = best_practices.get('error', False)
        
        # Calculate totals
        total_tokens = security.get('tokens', 0) + performance.get('tokens', 0) + best_practices.get('tokens', 0)
        total_cost = security.get('cost', 0) + performance.get('cost', 0) + best_practices.get('cost', 0)
        
        # Format combined review
        combined_review = format_combined_review(
            security, 
            performance, 
            best_practices,
            parse_statistics,
            context_statistics,
            total_tokens,
            total_cost
        )
        
        # Generate review ID
        review_id = f"review_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        # Store in DynamoDB
        review_item = {
            'review_id': review_id,
            'timestamp': timestamp,
            'repo_name': repo_name,
            'pr_number': pr_number,
            'combined_review': combined_review,
            'agent_results': {
                'security': {
                    'tokens': security.get('tokens', 0),
                    'cost': float(security.get('cost', 0)),
                    'error': security_error
                },
                'performance': {
                    'tokens': performance.get('tokens', 0),
                    'cost': float(performance.get('cost', 0)),
                    'error': performance_error
                },
                'best_practices': {
                    'tokens': best_practices.get('tokens', 0),
                    'cost': float(best_practices.get('cost', 0)),
                    'error': best_practices_error
                }
            },
            'totals': {
                'tokens': total_tokens,
                'cost': float(total_cost)
            },
            'statistics': {
                'parsed_files': parse_statistics.get('parsed_files', 0),
                'total_functions': parse_statistics.get('total_functions', 0),
                'total_classes': parse_statistics.get('total_classes', 0),
                'patterns_identified': context_statistics.get('total_patterns', 0)
            }
        }
        
        reviews_table.put_item(Item=review_item)
        
        print(f"✅ Review stored: {review_id}")
        print(f"📊 Total tokens: {total_tokens}")
        print(f"💰 Total cost: ${total_cost:.4f}")
        
        print("=" * 60)
        print("✅ Review Aggregator Complete")
        print("=" * 60)
        
        return {
            "statusCode": 200,
            "review_id": review_id,
            "combined_review": combined_review,
            "timestamp": timestamp,
            "totals": {
                "tokens": total_tokens,
                "cost": total_cost
            }
        }
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR in ReviewAggregator: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        return {
            "statusCode": 500,
            "error": str(e)
        }


def format_combined_review(security, performance, best_practices, parse_stats, context_stats, total_tokens, total_cost):
    """Format all agent reviews into a single markdown report"""
    
    # Header
    report = f"""## 🎯 Code Analysis Summary

**Analysis Completed:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

### 📊 Statistics
- **Files Analyzed:** {parse_stats.get('parsed_files', 0)}
- **Functions:** {parse_stats.get('total_functions', 0)}
- **Classes:** {parse_stats.get('total_classes', 0)}
- **Lines of Code:** {parse_stats.get('total_lines', 0)}
- **Patterns Identified:** {context_stats.get('total_patterns', 0)}
  - 🔒 Security: {context_stats.get('security_patterns', 0)}
  - ⚡ Performance: {context_stats.get('performance_patterns', 0)}
  - 📚 Quality: {context_stats.get('quality_patterns', 0)}

### 💰 Analysis Metrics
- **Total Tokens:** {total_tokens:,}
- **Total Cost:** ${total_cost:.4f} (FREE with Gemini! 🎉)

---

"""
    
    # Security Review
    if security.get('error'):
        report += f"""## 🔒 SECURITY ANALYSIS

⚠️ Security analysis encountered an error: {security.get('review', 'Unknown error')}

---

"""
    else:
        report += f"""{security.get('review', 'No security review available')}

---

"""
    
    # Performance Review
    if performance.get('error'):
        report += f"""## ⚡ PERFORMANCE ANALYSIS

⚠️ Performance analysis encountered an error: {performance.get('review', 'Unknown error')}

---

"""
    else:
        report += f"""{performance.get('review', 'No performance review available')}

---

"""
    
    # Best Practices Review
    if best_practices.get('error'):
        report += f"""## 📚 BEST PRACTICES ANALYSIS

⚠️ Best practices analysis encountered an error: {best_practices.get('review', 'Unknown error')}

---

"""
    else:
        report += f"""{best_practices.get('review', 'No best practices review available')}

---

"""
    
    # Footer
    report += f"""## 📝 Next Steps

1. Review the issues identified above, prioritizing by severity
2. Focus on 🔴 CRITICAL and 🟠 HIGH severity issues first
3. Implement the suggested fixes and improvements
4. Re-run the review after making changes

---

**🤖 Powered by AI Code Review Platform**  
*Using Google Gemini 2.5 Flash - 100% Free!*
"""
    
    return report
