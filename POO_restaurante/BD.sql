-- Crear base de datos
CREATE DATABASE restaurant_db;

-- Conectarse a ella
\c restaurant_db

-- Crear tabla menu
CREATE TABLE menu (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    precio NUMERIC(10,2) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla pedidos
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    mesa_numero INTEGER NOT NULL,
    numero_app INTEGER,
    estado VARCHAR(50) NOT NULL DEFAULT 'Pendiente',
    fecha_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    items JSONB NOT NULL,  -- ¡PostgreSQL soporta JSON nativo!
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_pedidos_estado ON pedidos(estado);
CREATE INDEX idx_pedidos_mesa ON pedidos(mesa_numero);
CREATE INDEX idx_menu_tipo ON menu(tipo);