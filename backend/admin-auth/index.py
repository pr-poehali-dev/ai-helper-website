import json
import os
import hashlib
from typing import Dict, Any

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: Authenticate admin user for ИИпомогатор
    Args: event with httpMethod, body with username and password
          context with request_id
    Returns: HTTP response with auth token and admin info
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    if method != 'POST':
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
        admin_password = os.environ.get('ADMIN_PASSWORD')
        
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
        username = body_data.get('username')
        password = body_data.get('password')
        
        if not username or not password:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Username and password required'})
            }
        
        if username != 'admin':
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Invalid credentials'})
            }
        
        if not admin_password or password != admin_password:
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Invalid credentials'})
            }
        
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute('''
            SELECT id, username, full_name
            FROM t_p94602577_ai_helper_website.admins
            WHERE username = %s
        ''', (username,))
        
        admin_data = cur.fetchone()
        
        if not admin_data:
            cur.close()
            conn.close()
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Admin not found'})
            }
        
        cur.execute('''
            UPDATE t_p94602577_ai_helper_website.admins
            SET last_login = CURRENT_TIMESTAMP
            WHERE username = %s
        ''', (username,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        admin_id, admin_username, full_name = admin_data
        
        token = hashlib.sha256(f'{admin_username}_{admin_password}'.encode()).hexdigest()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'isBase64Encoded': False,
            'body': json.dumps({
                'success': True,
                'token': token,
                'admin': {
                    'id': admin_id,
                    'username': admin_username,
                    'full_name': full_name
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