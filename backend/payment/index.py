import json
import os
import uuid
from typing import Dict, Any

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: Create YooKassa payment for AI requests packages
    Args: event with httpMethod, body with user_id, package_type, amount, description
          context with request_id
    Returns: HTTP response with payment URL and payment_id
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-User-Id',
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
        from yookassa import Configuration, Payment
        import psycopg2
        
        shop_id = os.environ.get('YOOKASSA_SHOP_ID')
        secret_key = os.environ.get('YOOKASSA_SECRET_KEY')
        db_url = os.environ.get('DATABASE_URL')
        
        if not shop_id or not secret_key:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Payment system not configured'})
            }
        
        if not db_url:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Database not configured'})
            }
        
        Configuration.account_id = shop_id
        Configuration.secret_key = secret_key
        
        body_data = json.loads(event.get('body', '{}'))
        user_id = body_data.get('user_id')
        package_type = body_data.get('package_type')
        amount = body_data.get('amount')
        description = body_data.get('description', 'Покупка запросов ИИпомогатор')
        requests_count = body_data.get('requests_count')
        
        if not all([user_id, package_type, amount, requests_count]):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing required fields'})
            }
        
        idempotence_key = str(uuid.uuid4())
        
        payment = Payment.create({
            'amount': {
                'value': str(amount),
                'currency': 'RUB'
            },
            'confirmation': {
                'type': 'redirect',
                'return_url': 'https://ai-helper-website.poehali.dev/?payment=success'
            },
            'capture': True,
            'description': description,
            'metadata': {
                'user_id': user_id,
                'package_type': package_type,
                'requests_count': str(requests_count)
            }
        }, idempotence_key)
        
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO t_p94602577_ai_helper_website.users (user_id)
            VALUES (%s)
            ON CONFLICT (user_id) DO NOTHING
        ''', (user_id,))
        
        cur.execute('''
            INSERT INTO t_p94602577_ai_helper_website.purchases 
            (user_id, package_type, requests_count, price_rub, payment_status, yookassa_payment_id, payment_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (user_id, package_type, requests_count, amount, 'pending', payment.id, payment.confirmation.confirmation_url))
        
        purchase_id = cur.fetchone()[0]
        
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
                'payment_id': payment.id,
                'payment_url': payment.confirmation.confirmation_url,
                'purchase_id': purchase_id,
                'status': payment.status
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