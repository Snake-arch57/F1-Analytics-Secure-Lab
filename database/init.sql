-- Script de inicialização do Banco de Dados F1 Analytics
CREATE TABLE IF NOT EXISTS team_performance (
    id SERIAL PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    season INT NOT NULL,
    avg_lap_time_seconds NUMERIC(8, 3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dados iniciais de demonstração
INSERT INTO team_performance (team_name, season, avg_lap_time_seconds) VALUES
('Red Bull Racing', 2024, 91.245),
('Ferrari', 2024, 91.510),
('McLaren', 2024, 91.430),
('Mercedes', 2024, 91.680)
ON CONFLICT DO NOTHING;
