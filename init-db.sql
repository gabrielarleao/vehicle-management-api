-- Banco de dados principal para gerenciamento de veículos
-- Este banco armazena veículos e dados de autenticação

-- Criar banco de autenticação separado
CREATE DATABASE tech_challenge_auth;

-- Tabela de veículos
CREATE TABLE IF NOT EXISTS vehicles (
    id SERIAL PRIMARY KEY,
    marca VARCHAR(100) NOT NULL,
    modelo VARCHAR(100) NOT NULL,
    ano INTEGER NOT NULL,
    cor VARCHAR(50) NOT NULL,
    preco DECIMAL(12, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'DISPONIVEL',
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para otimização
CREATE INDEX IF NOT EXISTS idx_vehicles_status ON vehicles(status);
CREATE INDEX IF NOT EXISTS idx_vehicles_preco ON vehicles(preco);
CREATE INDEX IF NOT EXISTS idx_vehicles_marca ON vehicles(marca);
CREATE INDEX IF NOT EXISTS idx_vehicles_modelo ON vehicles(modelo);
