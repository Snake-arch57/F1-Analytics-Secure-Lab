-- Script de inicializacao do Banco de Dados F1 Analytics
-- A tabela existe para compatibilidade: ai_context_view.sql a renomeia
-- para team_performance_base e cria a view team_performance no lugar.
-- Sem dados de demonstracao: numeros ficticios chegariam a IA como reais.
CREATE TABLE IF NOT EXISTS team_performance (
    id SERIAL PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    season INT NOT NULL,
    avg_lap_time_seconds NUMERIC(8, 3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
