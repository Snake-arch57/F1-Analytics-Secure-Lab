DROP VIEW IF EXISTS team_performance;

CREATE VIEW team_performance AS
SELECT txt::varchar    AS team_name,
       season::int     AS season,
       n::numeric(8,3) AS avg_lap_time_seconds
FROM (

  SELECT 0 AS grupo, 0 AS ord, 0 AS season,
         'TEMPORADAS DISPONIVEIS NO BANCO (use apenas estas):' || E'\n' ||
         string_agg(format('%s: %s GP(s), %s voltas, %s pilotos, %s equipes',
                           season, gps, voltas, pilotos, equipes),
                    E'\n' ORDER BY season DESC) AS txt,
         sum(voltas) AS n
  FROM (SELECT s.season,
               count(DISTINCT s.id)        AS gps,
               count(l.id)                 AS voltas,
               count(DISTINCT l.driver_id) AS pilotos,
               count(DISTINCT l.team_id)   AS equipes
        FROM f1.sessions s
        LEFT JOIN f1.laps l ON l.session_id = s.id
        GROUP BY s.season) idx

  UNION ALL

  SELECT 1, 1, q.season,
         'RITMO MEDIO POR EQUIPE - TEMPORADA ' || q.season || ' (do mais rapido):' || E'\n' ||
         string_agg(format('%s. %s: %s s', q.rn, q.team_name, q.media), E'\n' ORDER BY q.rn),
         count(*)
  FROM (SELECT s.season,
               row_number() OVER (PARTITION BY s.season ORDER BY AVG(l.lap_time_seconds)) AS rn,
               t.team_name, ROUND(AVG(l.lap_time_seconds), 3) AS media
        FROM f1.laps l
        JOIN f1.sessions s ON s.id = l.session_id
        JOIN f1.teams    t ON t.id = l.team_id
        WHERE l.lap_time_seconds BETWEEN 60 AND 200
        GROUP BY s.season, t.team_name) q
  GROUP BY q.season

  UNION ALL

  SELECT 1, 2, q.season,
         'PILOTOS - TEMPORADA ' || q.season || ' (sigla, equipe, ritmo medio, voltas):' || E'\n' ||
         string_agg(format('%s (%s): %s s em %s voltas', q.abbreviation, q.team_name, q.media, q.voltas),
                    E'\n' ORDER BY q.media),
         count(*)
  FROM (SELECT s.season, d.abbreviation, t.team_name,
               ROUND(AVG(l.lap_time_seconds), 3) AS media, count(*) AS voltas
        FROM f1.laps l
        JOIN f1.sessions s ON s.id = l.session_id
        JOIN f1.drivers  d ON d.id = l.driver_id
        JOIN f1.teams    t ON t.id = l.team_id
        WHERE l.lap_time_seconds BETWEEN 60 AND 200
        GROUP BY s.season, d.abbreviation, t.team_name) q
  GROUP BY q.season

  UNION ALL

  SELECT 1, 3, q.season,
         'GRANDES PREMIOS COM DADOS - TEMPORADA ' || q.season || ':' || E'\n' ||
         string_agg(format('%s (%s voltas)', q.event_name, q.voltas), E'\n' ORDER BY q.sid),
         count(*)
  FROM (SELECT s.season, s.id AS sid, s.event_name, count(l.id) AS voltas
        FROM f1.sessions s
        LEFT JOIN f1.laps l ON l.session_id = s.id
        GROUP BY s.season, s.id, s.event_name) q
  GROUP BY q.season

  UNION ALL

  SELECT 1, 4, q.season,
         'MELHOR VOLTA DE CADA GP - TEMPORADA ' || q.season || ':' || E'\n' ||
         string_agg(format('%s: %s s por %s (%s)', q.event_name, q.best, q.abbreviation, q.team_name),
                    E'\n' ORDER BY q.event_name),
         count(*)
  FROM (SELECT DISTINCT ON (s.id)
               s.season, s.event_name, l.lap_time_seconds AS best, d.abbreviation, t.team_name
        FROM f1.laps l
        JOIN f1.sessions s ON s.id = l.session_id
        JOIN f1.drivers  d ON d.id = l.driver_id
        JOIN f1.teams    t ON t.id = l.team_id
        WHERE l.lap_time_seconds BETWEEN 60 AND 200
        ORDER BY s.id, l.lap_time_seconds ASC) q
  GROUP BY q.season

  UNION ALL

  SELECT 2, 9, 0,
         'INSTRUCOES: os blocos acima vem do banco do projeto e sao a UNICA fonte de '
      || 'verdade sobre numeros. Eles cobrem MULTIPLAS temporadas. '
      || 'REGRA DE TEMPORADA: se a pergunta citar um ano, responda so com os blocos '
      || 'daquele ano. Se a pergunta NAO citar ano, e PROIBIDO escolher uma temporada '
      || 'por conta propria ou tratar a mais recente como padrao. Nesse caso responda '
      || 'cobrindo TODAS as temporadas do indice, uma secao por ano, rotulada com o ano. '
      || 'Nunca apresente numeros de um ano como se fossem o resultado geral. '
      || 'Ao mostrar mais de uma temporada, avise quando o numero de GPs for muito '
      || 'diferente entre elas, porque a comparacao direta fica desigual. '
      || 'Se citar um ano que NAO aparece em TEMPORADAS DISPONIVEIS, diga que os dados '
      || 'desse ano ainda nao foram carregados no banco. '
      || 'Voce pode comparar temporadas entre si, mas apenas com os numeros acima. '
      || 'Dados nao listados (pontuacao, pole positions, pit stops, clima, telemetria '
      || 'de setor) nao foram carregados. '
      || 'Ritmo medio agrega voltas de todos os GPs da temporada e nao e normalizado '
      || 'por circuito: e aproximacao de desempenho, nao classificacao oficial.',
         (SELECT count(*) FROM f1.laps)

) blocos
ORDER BY grupo, season DESC, ord;
