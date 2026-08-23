-- ============================================================
-- SUPABASE SCHEMA - Hotel Logbook
-- ============================================================
-- Ejecuta este SQL en el SQL Editor de tu proyecto Supabase
-- (SQL Editor > New query > Run)

-- Tabla principal de solicitudes
CREATE TABLE IF NOT EXISTS requests (
    id SERIAL PRIMARY KEY,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    room TEXT NOT NULL,
    operator TEXT NOT NULL,
    request_type TEXT NOT NULL,
    notes TEXT DEFAULT '—',
    status TEXT DEFAULT 'Open',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de operadores
CREATE TABLE IF NOT EXISTS operators (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de tipos de solicitud
CREATE TABLE IF NOT EXISTS request_types (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insertar operadores por defecto
INSERT INTO operators (name) VALUES
    ('Fred Wayne'),
    ('Maria Garcia'),
    ('John Smith'),
    ('Sarah Chen')
ON CONFLICT (name) DO NOTHING;

-- Insertar tipos de solicitud por defecto
INSERT INTO request_types (name) VALUES
    ('Housekeeping'),
    ('Maintenance'),
    ('Room Service'),
    ('Concierge'),
    ('Transportation'),
    ('Spa & Wellness'),
    ('Restaurant Reservation'),
    ('Laundry'),
    ('Wake-up Call'),
    ('Complaint'),
    ('Other')
ON CONFLICT (name) DO NOTHING;

-- Crear índices para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_requests_date ON requests(date);
CREATE INDEX IF NOT EXISTS idx_requests_room ON requests(room);
CREATE INDEX IF NOT EXISTS idx_requests_operator ON requests(operator);
CREATE INDEX IF NOT EXISTS idx_requests_type ON requests(request_type);
CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(status);
