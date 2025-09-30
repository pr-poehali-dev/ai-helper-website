-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    full_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    free_requests_used INTEGER DEFAULT 0,
    paid_requests_available INTEGER DEFAULT 0,
    last_free_request_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы сообщений чата
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы покупок
CREATE TABLE IF NOT EXISTS purchases (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    package_type VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    requests_count INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    payment_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Создание таблицы администраторов
CREATE TABLE IF NOT EXISTS admins (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание первого администратора (логин: creator, пароль: creator2024)
INSERT INTO admins (username, password_hash, full_name)
VALUES ('creator', '$2b$10$xYzAbC123ExampleHashForCreator2024PasswdHere', 'Создатель')
ON CONFLICT (username) DO NOTHING;