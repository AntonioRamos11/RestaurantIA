-- Crear tabla menu (SOLO UNA VEZ)

CREATE TABLE menu (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    precio NUMERIC(10,2) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE DATABASE restaurant_db

-- Crear tabla pedidos (SOLO UNA VEZ)
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    mesa_numero INTEGER NOT NULL,
    numero_app INTEGER,
    estado VARCHAR(50) NOT NULL DEFAULT 'Pendiente',
    fecha_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    items JSONB NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para mejorar rendimiento (SOLO UNA VEZ)
CREATE INDEX idx_pedidos_estado ON pedidos(estado);
CREATE INDEX idx_pedidos_mesa ON pedidos(mesa_numero);
CREATE INDEX idx_menu_tipo ON menu(tipo);


-- Eliminar todos los ítems existentes
DELETE FROM menu;

-- Insertar todos los ítems del menú
INSERT INTO menu (nombre, precio, tipo) VALUES
-- Entradas
('Empanada Kunai', 70.00, 'Entradas'),
('Dedos de queso (5pz)', 75.00, 'Entradas'),
('Chile Relleno', 60.00, 'Entradas'),
('Caribe Poppers', 130.00, 'Entradas'),
('Brocheta', 50.00, 'Entradas'),
('Rollos Primavera (2pz)', 100.00, 'Entradas'),
-- Platillos
('Camarones roca', 160.00, 'Platillos'),
('Teriyaki', 130.00, 'Platillos'),
('Bonneles (300gr)', 150.00, 'Platillos'),
-- Arroces
('Yakimeshi Especial', 150.00, 'Arroces'),
('Yakimeshi Kunai', 140.00, 'Arroces'),
('Yakimeshi Golden', 145.00, 'Arroces'),
('Yakimeshi Horneado', 145.00, 'Arroces'),
('Gohan Mixto', 125.00, 'Arroces'),
('Gohan Crispy', 125.00, 'Arroces'),
('Gohan Chicken', 120.00, 'Arroces'),
('Kunai Burguer', 140.00, 'Arroces'),
('Bomba', 105.00, 'Arroces'),
('Bomba Especial', 135.00, 'Arroces'),
-- Naturales
('Guamuchilito', 110.00, 'Naturales'),
('Avocado', 125.00, 'Naturales'),
('Grenudo Roll', 135.00, 'Naturales'),
('Granja Roll', 115.00, 'Naturales'),
('California Roll', 100.00, 'Naturales'),
('California Especial', 130.00, 'Naturales'),
('Arcoíris', 120.00, 'Naturales'),
('Tuna Roll', 130.00, 'Naturales'),
('Kusanagi', 130.00, 'Naturales'),
('Kanisweet', 120.00, 'Naturales'),
-- Empanizados
('Mar y Tierra', 95.00, 'Empanizados'),
('Tres Quesos', 100.00, 'Empanizados'),
('Cordon Blue', 105.00, 'Empanizados'),
('Roka Roll', 135.00, 'Empanizados'),
('Camarón Bacon', 110.00, 'Empanizados'),
('Cielo, mar y tierra', 110.00, 'Empanizados'),
('Konan Roll', 130.00, 'Empanizados'),
('Pain Roll', 115.00, 'Empanizados'),
('Sasori Roll', 125.00, 'Empanizados'),
('Chikin', 130.00, 'Empanizados'),
('Caribe Roll', 115.00, 'Empanizados'),
('Chon', 120.00, 'Empanizados'),
-- Gratinados
('Kunai Especial', 150.00, 'Gratinados'),
('Chuma Roll', 145.00, 'Gratinados'),
('Choche Roll', 140.00, 'Gratinados'),
('Milán Roll', 135.00, 'Gratinados'),
('Chio Roll', 145.00, 'Gratinados'),
('Prime', 140.00, 'Gratinados'),
('Ninja Roll', 135.00, 'Gratinados'),
('Serranito', 135.00, 'Gratinados'),
('Sanji', 145.00, 'Gratinados'),
('Monkey Roll', 135.00, 'Gratinados'),
-- Kunai Kids
('Baby Roll (8pz)', 60.00, 'Kunai Kids'),
('Chicken Sweet (7pz)', 60.00, 'Kunai Kids'),
('Chesse Puffs (10pz)', 55.00, 'Kunai Kids'),
-- Bebidas
('Te refil', 35.00, 'Bebidas'),
('Te de litro', 35.00, 'Bebidas'),
('Coca-cola', 35.00, 'Bebidas'),
('Agua natural', 20.00, 'Bebidas'),
('Agua mineral', 35.00, 'Bebidas'),
-- Extras
('Camaron', 20.00, 'Extras'),
('Res', 15.00, 'Extras'),
('Pollo', 15.00, 'Extras'),
('Tocino', 15.00, 'Extras'),
('Gratinado', 15.00, 'Extras'),
('Aguacate', 25.00, 'Extras'),
('Empanizado', 15.00, 'Extras'),
('Philadelphia', 10.00, 'Extras'),
('Tampico', 25.00, 'Extras'),
('Siracha', 10.00, 'Extras'),
('Soya', 10.00, 'Extras');



CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    domicilio TEXT,
    celular VARCHAR(20),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);