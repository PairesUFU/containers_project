-- Extensão para UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Usuários e sessões
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sessions (
    session_key UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES users(id),
    ip TEXT,
    expires_at TIMESTAMP
);

-- Aeroportos
CREATE TABLE airports (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    city TEXT NOT NULL
);

-- Voos
CREATE TABLE flights (
    id SERIAL PRIMARY KEY,
    flight_number TEXT NOT NULL,
    origin_id INTEGER REFERENCES airports(id),
    destination_id INTEGER REFERENCES airports(id),
    departure_time TIMESTAMP,
    arrival_time TIMESTAMP,
    price NUMERIC
);

-- Reservas e tickets
CREATE TABLE reservations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    flight_id INTEGER REFERENCES flights(id),
    reserved_at TIMESTAMP DEFAULT NOW(),
    locator TEXT
);

CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    reservation_id INTEGER REFERENCES reservations(id),
    ticket_number TEXT UNIQUE NOT NULL
);

-- Inserções
INSERT INTO users (email, password) VALUES ('teste@ex.com','123456');

INSERT INTO airports (code,   name,                 city) VALUES
  ('GRU', 'Aeroporto de Guarulhos',    'São Paulo'),
  ('GIG', 'Aeroporto do Galeão',       'Rio de Janeiro'),
  ('BSB', 'Aeroporto Internacional de Brasília', 'Brasília');

INSERT INTO flights (
  flight_number, origin_id, destination_id,
  departure_time,      arrival_time,       price
) VALUES
  ('AZ123', 1, 2, '2025-05-10 08:00:00', '2025-05-10 10:00:00', 350.50),
  ('AZ456', 2, 1, '2025-05-10 12:30:00', '2025-05-10 14:30:00', 330.00),
  ('BS789', 3, 1, '2025-05-11 09:00:00', '2025-05-11 11:00:00', 400.00);