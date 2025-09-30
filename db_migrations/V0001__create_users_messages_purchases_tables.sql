CREATE TABLE t_p94602577_ai_helper_website.users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    free_requests_used INTEGER DEFAULT 0,
    free_requests_reset_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_requests_available INTEGER DEFAULT 0
);

CREATE INDEX idx_users_user_id ON t_p94602577_ai_helper_website.users(user_id);

CREATE TABLE t_p94602577_ai_helper_website.chat_messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    model VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_user_id ON t_p94602577_ai_helper_website.chat_messages(user_id);
CREATE INDEX idx_messages_created_at ON t_p94602577_ai_helper_website.chat_messages(created_at);

CREATE TABLE t_p94602577_ai_helper_website.purchases (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    package_type VARCHAR(50) NOT NULL,
    requests_count INTEGER NOT NULL,
    price_rub INTEGER NOT NULL,
    payment_status VARCHAR(50) DEFAULT 'pending',
    payment_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_purchases_user_id ON t_p94602577_ai_helper_website.purchases(user_id);
CREATE INDEX idx_purchases_payment_status ON t_p94602577_ai_helper_website.purchases(payment_status);