-- Contexto da IA: blocos de texto ja formatados, sem ano fixo.
-- A temporada alvo e sempre a mais recente presente em f1.sessions.

-- Renomeia a tabela do init.sql apenas na primeira execucao (idempotente).
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables
             WHERE table_schema = 'public'
               AND table_name = 'team_performance'
               AND table_type = 'BASE TABLE') THEN
    ALTER TABLE team_performance RENAME TO team_performance_base;
  END IF;
END $$;

DROP VIEW IF EXISTS team_performance;

CREATE VIEW team_performance AS
WITH alvo AS (
  SELECT COALESCE(MAX(season), EXTRACT(YEAR FROM now())::int) AS season
  FROM f1.sessions
),
ranking AS (
  SELECT 'RITMO MEDIO POR EQUIPE (' || (SELECT season FROM alvo)
         || ', ordenado do mais rapido):' || E'\n' ||
         string_agg(format('%s. %s: %s s', rn, team_name, media), E'\n' ORDER BY rn) AS txt,
         count(*) AS n
  FROM (SELECT row_number() OVER (ORDER BY AVG(l.lap_time_seconds)) AS rn,
               t.team_name, ROUND(AVG(l.lap_time_seconds), 3) AS media
        FROM f1.laps l
        JOIN f1.sessions s ON s.id = l.session_id
        JOIN f1.teams    t ON t.id = l.team_id
        WHERE s.season = (SELECT season FROM alvo)
          AND l.lap_time_seconds BETWEEN 60 AND 200
        GROUP BY t.team_name) q
),
pilotos AS (
  SELECT 'PILOTOS ' || (SELECT season FROM alvo)
         || ' (sigla, equipe, ritmo medio, voltas):' || E'\n' ||
         string_agg(format('%s (%s): %s s em %s voltas', abbreviation, team_name, media, voltas),
                    E'\n' ORDER BY media) AS txt,
         count(*) AS n
  FROM (SELECT d.abbreviation, t.team_name,
               ROUND(AVG(l.lap_time_seconds), 3) AS media,
               count(*) AS voltas
        FROM f1.laps l
        JOIN f1.sessions s ON s.id = l.session_id
        JOIN f1.drivers  d ON d.id = l.driver_id
        JOIN f1.teams    t ON t.id = l.team_id
        WHERE s.season = (SELECT season FROM alvo)
          AND l.lap_time_seconds BETWEEN 60 AND 200
        GROUP BY d.abbreviation, t.team_name) q
),
gps AS (
  SELECT 'GRANDES PREMIOS COM DADOS CARREGADOS (' || (SELECT season FROM alvo) || '):' || E'\n' ||
         string_agg(format('%s (%s voltas)', event_name, voltas), E'\n' ORDER BY sid) AS txt,
         count(*) AS n
  FROM (SELECT s.id AS sid, s.event_name, count(l.id) AS voltas
        FROM f1.sessions s
        LEFT JOIN f1.laps l ON l.session_id = s.id
        WHERE s.season = (SELECT season FROM alvo)
        GROUP BY s.id, s.event_name) q
),
destaques AS (
  SELECT 'MELHOR VOLTA DE CADA GP (' || (SELECT season FROM alvo) || '):' || E'\n' ||
         string_agg(format('%s: %s s por %s (%s)', event_name, best, abbreviation, team_name),
                    E'\n' ORDER BY event_name) AS txt,
         count(*) AS n
  FROM (SELECT DISTINCT ON (s.id)
               s.event_name, l.lap_time_seconds AS best, d.abbreviation, t.team_name
        FROM f1.laps l
        JOIN f1.sessions s ON s.id = l.session_id
        JOIN f1.drivers  d ON d.id = l.driver_id
        JOIN f1.teams    t ON t.id = l.team_id
        WHERE s.season = (SELECT season FROM alvo)
          AND l.lap_time_seconds BETWEEN 60 AND 200
        ORDER BY s.id, l.lap_time_seconds ASC) q
),
meta AS (
  SELECT 'INSTRUCOES: os dados acima vem do banco do projeto e sao a fonte de '
      || 'verdade sobre a temporada ' || (SELECT season FROM alvo) || '. '
      || 'Use-os em vez de conhecimento proprio. Se a pergunta exigir algo que '
      || 'nao esta listado (pontuacao, pole positions, pit stops), diga que esse '
      || 'dado ainda nao foi carregado. Ritmo medio inclui voltas de todos os GPs '
      || 'e nao e normalizado por circuito, entao serve como aproximacao. '
      || 'Ultima atualizacao: ' || to_char(now(), 'DD/MM/YYYY HH24:MI') AS txt,
         (SELECT count(*) FROM f1.laps l
          JOIN f1.sessions s ON s.id = l.session_id
          WHERE s.season = (SELECT season FROM alvo)) AS n
)
SELECT txt::varchar AS team_name,
       (SELECT season FROM alvo)::int AS season,
       n::numeric(8,3) AS avg_lap_time_seconds
FROM ranking
UNION ALL SELECT txt::varchar, (SELECT season FROM alvo)::int, n::numeric(8,3) FROM pilotos
UNION ALL SELECT txt::varchar, (SELECT season FROM alvo)::int, n::numeric(8,3) FROM gps
UNION ALL SELECT txt::varchar, (SELECT season FROM alvo)::int, n::numeric(8,3) FROM destaques
UNION ALL SELECT txt::varchar, (SELECT season FROM alvo)::int, n::numeric(8,3) FROM meta;
