'''
Business: Handle AI chat with guest (10) and registered (15) user limits
Args: event with httpMethod, body with message and user_id, headers with X-User-Token
Returns: HTTP response with AI reply and usage stats
'''

import json
import os
import jwt
from typing import Dict, Any
from datetime import datetime, timedelta

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-User-Token',
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
        from psycopg2.extras import RealDictCursor
        
        api_key = os.environ.get('OPENAI_API_KEY')
        db_url = os.environ.get('DATABASE_URL')
        jwt_secret = os.environ.get('JWT_SECRET', 'default-secret')
        
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
        user_id_from_body = body_data.get('user_id', '')
        
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
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        is_guest = user_id_from_body.startswith('guest_')
        user_id = None
        free_limit = 10
        
        if not is_guest:
            headers = event.get('headers', {})
            token = headers.get('X-User-Token') or headers.get('x-user-token')
            
            if token:
                try:
                    decoded = jwt.decode(token, jwt_secret, algorithms=['HS256'])
                    user_id = decoded.get('user_id')
                    free_limit = 15
                except:
                    pass
        
        if is_guest:
            guest_key = f'guest:{user_id_from_body}'
            cur.execute(
                "SELECT COUNT(*) as count FROM messages WHERE user_id = 0 AND content LIKE %s AND created_at > NOW() - INTERVAL '24 hours'",
                (f'{guest_key}%',)
            )
            result = cur.fetchone()
            guest_requests_today = result['count'] if result else 0
            
            if guest_requests_today >= 10:
                conn.close()
                return {
                    'statusCode': 429,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Лимит гостевых запросов исчерпан (10/день). Зарегистрируйтесь и получите +5 запросов!',
                        'usage': {
                            'free_requests_used': guest_requests_today,
                            'paid_requests_available': 0
                        }
                    })
                }
        else:
            if not user_id:
                conn.close()
                return {
                    'statusCode': 401,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Authentication required'})
                }
            
            cur.execute(
                "SELECT free_requests_used, paid_requests_available, last_free_request_reset FROM users WHERE id = %s",
                (user_id,)
            )
            user_data = cur.fetchone()
            
            if not user_data:
                conn.close()
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'User not found'})
                }
            
            free_used = user_data['free_requests_used']
            paid_available = user_data['paid_requests_available']
            last_reset = user_data['last_free_request_reset']
            
            if last_reset and (datetime.now() - last_reset).days >= 1:
                cur.execute(
                    "UPDATE users SET free_requests_used = 0, last_free_request_reset = NOW() WHERE id = %s",
                    (user_id,)
                )
                conn.commit()
                free_used = 0
            
            if free_used >= 15 and paid_available <= 0:
                conn.close()
                return {
                    'statusCode': 429,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Бесплатные запросы исчерпаны. Купите дополнительные запросы!',
                        'usage': {
                            'free_requests_used': free_used,
                            'paid_requests_available': paid_available
                        }
                    })
                }
            
            if free_used < 15:
                cur.execute(
                    "UPDATE users SET free_requests_used = free_requests_used + 1 WHERE id = %s",
                    (user_id,)
                )
            else:
                cur.execute(
                    "UPDATE users SET paid_requests_available = paid_requests_available - 1 WHERE id = %s",
                    (user_id,)
                )
            
            conn.commit()
        
        client = openai.OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': 'Ты - полезный ИИ-помощник. Отвечай на вопросы пользователей четко и по делу.'},
                {'role': 'user', 'content': user_message}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        ai_reply = completion.choices[0].message.content
        
        if is_guest:
            guest_key = f'guest:{user_id_from_body}'
            cur.execute(
                "INSERT INTO messages (user_id, role, content) VALUES (0, 'user', %s)",
                (f'{guest_key}:{user_message}',)
            )
            cur.execute(
                "INSERT INTO messages (user_id, role, content) VALUES (0, 'assistant', %s)",
                (f'{guest_key}:{ai_reply}',)
            )
            conn.commit()
            
            cur.execute(
                "SELECT COUNT(*) as count FROM messages WHERE user_id = 0 AND content LIKE %s AND created_at > NOW() - INTERVAL '24 hours'",
                (f'{guest_key}%',)
            )
            result = cur.fetchone()
            guest_requests_today = result['count'] // 2 if result else 0
            
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
                    'usage': {
                        'free_requests_used': guest_requests_today,
                        'paid_requests_available': 0
                    }
                })
            }
        else:
            cur.execute(
                "INSERT INTO messages (user_id, role, content) VALUES (%s, 'user', %s)",
                (user_id, user_message)
            )
            cur.execute(
                "INSERT INTO messages (user_id, role, content) VALUES (%s, 'assistant', %s)",
                (user_id, ai_reply)
            )
            conn.commit()
            
            cur.execute(
                "SELECT free_requests_used, paid_requests_available FROM users WHERE id = %s",
                (user_id,)
            )
            updated_user = cur.fetchone()
            
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
                    'usage': {
                        'free_requests_used': updated_user['free_requests_used'],
                        'paid_requests_available': updated_user['paid_requests_available']
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
            'body': json.dumps({'error': f'Server error: {str(e)}'})
        }