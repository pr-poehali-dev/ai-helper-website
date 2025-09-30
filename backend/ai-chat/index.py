import json
import os
from typing import Dict, Any
from datetime import datetime, timedelta

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: Handle AI chat requests with user tracking and request limits
    Args: event with httpMethod, body with message and user_id, headers with X-User-Id
          context with request_id
    Returns: HTTP response with AI reply and usage stats
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
        import openai
        import psycopg2
        
        api_key = os.environ.get('OPENAI_API_KEY')
        db_url = os.environ.get('DATABASE_URL')
        
        if not api_key:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'OpenAI API key not configured'})
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
        
        body_data = json.loads(event.get('body', '{}'))
        user_message = body_data.get('message', '')
        user_id = body_data.get('user_id') or event.get('headers', {}).get('X-User-Id', 'anonymous')
        
        if not user_message:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Message is required'})
            }
        
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO t_p94602577_ai_helper_website.users (user_id, last_active)
            VALUES (%s, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id) 
            DO UPDATE SET last_active = CURRENT_TIMESTAMP
            RETURNING free_requests_used, free_requests_reset_at, paid_requests_available
        ''', (user_id,))
        
        user_data = cur.fetchone()
        free_used, reset_at, paid_available = user_data
        
        now = datetime.now()
        reset_time = reset_at
        
        if now >= reset_time + timedelta(days=1):
            cur.execute('''
                UPDATE t_p94602577_ai_helper_website.users
                SET free_requests_used = 0, free_requests_reset_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            ''', (user_id,))
            free_used = 0
        
        if free_used >= 15 and paid_available <= 0:
            cur.close()
            conn.close()
            return {
                'statusCode': 429,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Request limit reached',
                    'free_requests_used': free_used,
                    'paid_requests_available': paid_available
                })
            }
        
        client = openai.OpenAI(api_key=api_key)
        
        cur.execute('''
            SELECT role, content FROM t_p94602577_ai_helper_website.chat_messages
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 10
        ''', (user_id,))
        
        history_rows = cur.fetchall()
        history_rows.reverse()
        
        messages = [
            {
                'role': 'system',
                'content': 'Ты — ИИпомогатор, дружелюбный и умный ассистент. Отвечай кратко, по существу и полезно. Используй русский язык.'
            }
        ]
        
        for role, content in history_rows:
            messages.append({'role': role, 'content': content})
        
        messages.append({'role': 'user', 'content': user_message})
        
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_reply = response.choices[0].message.content
        
        cur.execute('''
            INSERT INTO t_p94602577_ai_helper_website.chat_messages (user_id, role, content, model)
            VALUES (%s, %s, %s, %s)
        ''', (user_id, 'user', user_message, 'gpt-4o-mini'))
        
        cur.execute('''
            INSERT INTO t_p94602577_ai_helper_website.chat_messages (user_id, role, content, model)
            VALUES (%s, %s, %s, %s)
        ''', (user_id, 'assistant', ai_reply, 'gpt-4o-mini'))
        
        if free_used < 15:
            cur.execute('''
                UPDATE t_p94602577_ai_helper_website.users
                SET free_requests_used = free_requests_used + 1
                WHERE user_id = %s
            ''', (user_id,))
            new_free_used = free_used + 1
            new_paid_available = paid_available
        else:
            cur.execute('''
                UPDATE t_p94602577_ai_helper_website.users
                SET paid_requests_available = paid_requests_available - 1
                WHERE user_id = %s
            ''', (user_id,))
            new_free_used = free_used
            new_paid_available = paid_available - 1
        
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
                'reply': ai_reply,
                'model': 'gpt-4o-mini',
                'usage': {
                    'free_requests_used': new_free_used,
                    'free_requests_remaining': max(0, 15 - new_free_used),
                    'paid_requests_available': new_paid_available
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