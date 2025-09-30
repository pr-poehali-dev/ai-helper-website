import json
import os
from typing import Dict, Any

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: Get statistics for admin panel
    Args: event with httpMethod, headers with X-Admin-Token
          context with request_id
    Returns: HTTP response with users count, messages count, revenue
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-Admin-Token',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    if method != 'GET':
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        import psycopg2
        
        db_url = os.environ.get('DATABASE_URL')
        
        if not db_url:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Database not configured'})
            }
        
        headers = event.get('headers', {})
        admin_token = headers.get('X-Admin-Token') or headers.get('x-admin-token')
        
        if not admin_token:
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Admin token required'})
            }
        
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute('SELECT COUNT(*) FROM t_p94602577_ai_helper_website.users')
        users_count = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM t_p94602577_ai_helper_website.chat_messages')
        messages_count = cur.fetchone()[0]
        
        cur.execute('''
            SELECT 
                COUNT(*) as total_purchases,
                COALESCE(SUM(price_rub), 0) as total_revenue,
                COALESCE(SUM(CASE WHEN payment_status = 'completed' THEN price_rub ELSE 0 END), 0) as completed_revenue
            FROM t_p94602577_ai_helper_website.purchases
        ''')
        
        purchase_data = cur.fetchone()
        total_purchases = purchase_data[0]
        total_revenue = float(purchase_data[1])
        completed_revenue = float(purchase_data[2])
        
        cur.execute('''
            SELECT 
                package_type,
                COUNT(*) as count,
                SUM(price_rub) as revenue
            FROM t_p94602577_ai_helper_website.purchases
            WHERE payment_status = 'completed'
            GROUP BY package_type
        ''')
        
        packages_stats = []
        for row in cur.fetchall():
            packages_stats.append({
                'package': row[0],
                'count': row[1],
                'revenue': float(row[2])
            })
        
        cur.execute('''
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM t_p94602577_ai_helper_website.users
            WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            LIMIT 30
        ''')
        
        new_users_by_day = []
        for row in cur.fetchall():
            new_users_by_day.append({
                'date': row[0].isoformat(),
                'count': row[1]
            })
        
        cur.execute('''
            SELECT 
                COALESCE(SUM(free_requests_used), 0) as total_free,
                COALESCE(SUM(paid_requests_available), 0) as total_paid_remaining
            FROM t_p94602577_ai_helper_website.users
        ''')
        
        requests_data = cur.fetchone()
        total_free_used = requests_data[0]
        total_paid_remaining = requests_data[1]
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'isBase64Encoded': False,
            'body': json.dumps({
                'users': {
                    'total': users_count,
                    'new_by_day': new_users_by_day
                },
                'messages': {
                    'total': messages_count
                },
                'revenue': {
                    'total': completed_revenue,
                    'pending': total_revenue - completed_revenue,
                    'by_package': packages_stats
                },
                'purchases': {
                    'total': total_purchases
                },
                'requests': {
                    'free_used': total_free_used,
                    'paid_remaining': total_paid_remaining
                }
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Internal error: {str(e)}'})
        }