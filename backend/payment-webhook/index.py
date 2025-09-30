import json
import os
from typing import Dict, Any

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: Handle YooKassa payment webhooks to complete purchases
    Args: event with httpMethod, body with YooKassa notification
          context with request_id
    Returns: HTTP response with acknowledgment
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
        
        notification_type = body_data.get('event')
        payment_obj = body_data.get('object', {})
        
        if notification_type != 'payment.succeeded':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'status': 'ignored'})
            }
        
        payment_id = payment_obj.get('id')
        payment_status = payment_obj.get('status')
        metadata = payment_obj.get('metadata', {})
        
        user_id = metadata.get('user_id')
        requests_count = int(metadata.get('requests_count', 0))
        
        if not payment_id or not user_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Invalid webhook data'})
            }
        
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute('''
            UPDATE t_p94602577_ai_helper_website.purchases
            SET payment_status = %s
            WHERE yookassa_payment_id = %s AND payment_status = 'pending'
            RETURNING id
        ''', ('completed', payment_id))
        
        updated = cur.fetchone()
        
        if updated:
            cur.execute('''
                UPDATE t_p94602577_ai_helper_website.users
                SET paid_requests_available = paid_requests_available + %s
                WHERE user_id = %s
            ''', (requests_count, user_id))
        
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
            'body': json.dumps({'status': 'ok'})
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