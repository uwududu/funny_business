-- ============================================================
-- SCRIPT DE CRIAÇÃO DO BANCO DE DADOS E TABELA (MYSQL)
-- ============================================================

-- 1. Criação do Banco de Dados
CREATE DATABASE IF NOT EXISTS db_logs_teclado
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 2. Seleção do Banco
USE db_logs_teclado;

-- 3. Criação da Tabela para armazenar os logs processados
CREATE TABLE IF NOT EXISTS logs_traduzidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_arquivo VARCHAR(255) NOT NULL,
    data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    modo VARCHAR(50) NOT NULL,
    conteudo_traduzido LONGTEXT NOT NULL,
    conteudo_bruto LONGTEXT,
    INDEX idx_nome_arquivo (nome_arquivo),
    INDEX idx_data_registro (data_registro)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
