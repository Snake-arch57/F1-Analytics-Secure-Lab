BEGIN;
TRUNCATE team_performance_base RESTART IDENTITY;

-- O ORDER BY define a ordem fisica das linhas. Como o chat_controller.py faz
-- "SELECT ... LIMIT 5" sem ORDER BY, a IA recebe as 5 equipes mais rapidas.
INSERT INTO team_performance_base (team_name, season, avg_lap_time_seconds)
SELECT t.team_name, s.season, ROUND(AVG(l.lap_time_seconds)::numeric, 3)
FROM f1.laps l
JOIN f1.sessions s ON s.id = l.session_id
JOIN f1.teams    t ON t.id = l.team_id
WHERE s.season = 2026
  AND s.session_type = 'R'
  AND l.lap_time_seconds BETWEEN 60 AND 200
GROUP BY t.team_name, s.season
ORDER BY AVG(l.lap_time_seconds) ASC;
COMMIT;
