import json
import os
from typing import Dict, Any

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: Handle purchase of additional AI requests
    Args: event with httpMethod, body with user_id, package_type, requests_count, price_rub
          context with request_id
    Returns: HTTP response with purchase confirmation
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-User-Id',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    if method == 'POST':
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
            
            body_data = json.loads(event.get('body', '{}'))
            user_id = body_data.get('user_id')
            package_type = body_data.get('package_type')
            requests_count = body_data.get('requests_count')
            price_rub = body_data.get('price_rub')
            
            if not all([user_id, package_type, requests_count, price_rub]):
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Missing required fields'})
                }
            
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()
            
            cur.execute('''
                INSERT INTO t_p94602577_ai_helper_website.users (user_id)
                VALUES (%s)
                ON CONFLICT (user_id) DO NOTHING
            ''', (user_id,))
            
            cur.execute('''
                INSERT INTO t_p94602577_ai_helper_website.purchases 
                (user_id, package_type, requests_count, price_rub, payment_status)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            ''', (user_id, package_type, requests_count, price_rub, 'completed'))
            
            purchase_id = cur.fetchone()[0]
            
            cur.execute('''
                UPDATE t_p94602577_ai_helper_website.users
                SET paid_requests_available = paid_requests_available + %s
                WHERE user_id = %s
                RETURNING paid_requests_available
            ''', (requests_count, user_id))
            
            result = cur.fetchone()
            new_paid_balance = result[0] if result else requests_count
            
            conn.commit()
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
                    'success': True,
                    'purchase_id': purchase_id,
                    'paid_requests_available': new_paid_balance,
                    'message': f'Успешно куплено {requests_count} запросов'
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
    
    elif method == 'GET':
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
            
            query_params = event.get('queryStringParameters', {})
            user_id = query_params.get('user_id')
            
            if not user_id:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'user_id is required'})
                }
            
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()
            
            cur.execute('''
                SELECT 
                    free_requests_used,
                    paid_requests_available,
                    free_requests_reset_at
                FROM t_p94602577_ai_helper_website.users
                WHERE user_id = %s
            ''', (user_id,))
            
            result = cur.fetchone()
            
            if not result:
                cur.execute('''
                    INSERT INTO t_p94602577_ai_helper_website.users (user_id)
                    VALUES (%s)
                    RETURNING free_requests_used, paid_requests_available, free_requests_reset_at
                ''', (user_id,))
                result = cur.fetchone()
                conn.commit()
            
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
                    'free_requests_used': result[0],
                    'free_requests_remaining': max(0, 15 - result[0]),
                    'paid_requests_available': result[1],
                    'reset_at': result[2].isoformat()
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
    
    return {
        'statusCode': 405,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'error': 'Method not allowed'})
    }