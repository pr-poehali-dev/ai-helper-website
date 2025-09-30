-- Обновление таблицы администраторов с правильным хэшем для пароля creator2024
UPDATE admins 
SET password_hash = '$2b$12$Ld9h3BXxzYyNJMvWE1IpWe7xQ8qRnDKvJ7wRtUz9ZQKJh4dVxYJN6'
WHERE username = 'creator';

-- Если записи нет, создаём
INSERT INTO admins (username, password_hash, full_name)
SELECT 'creator', '$2b$12$Ld9h3BXxzYyNJMvWE1IpWe7xQ8qRnDKvJ7wRtUz9ZQKJh4dVxYJN6', 'Создатель'
WHERE NOT EXISTS (SELECT 1 FROM admins WHERE username = 'creator');