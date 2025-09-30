CREATE TABLE t_p94602577_ai_helper_website.admins (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

INSERT INTO t_p94602577_ai_helper_website.admins (username, password_hash, full_name)
VALUES ('admin', 'placeholder_hash', 'Егор Селицкий');

ALTER TABLE t_p94602577_ai_helper_website.purchases 
ADD COLUMN yookassa_payment_id VARCHAR(255),
ADD COLUMN payment_url TEXT;