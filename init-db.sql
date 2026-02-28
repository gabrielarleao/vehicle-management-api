-- Banco de dados principal para gerenciamento de veículos
-- Este banco armazena veículos e dados de autenticação

-- Criar banco de autenticação separado
CREATE DATABASE tech_challenge_auth;

-- As tabelas são criadas automaticamente pelo SQLAlchemy no startup da aplicação.
-- Isso garante que os tipos (como Enum) fiquem consistentes entre o ORM e o banco.
