CREATE SCHEMA IF NOT EXISTS f1 AUTHORIZATION f1_app;

CREATE TABLE IF NOT EXISTS f1.sessions (
    id           SERIAL PRIMARY KEY,
    season       INTEGER      NOT NULL,
    event_name   VARCHAR(150) NOT NULL,
    session_type VARCHAR(10)  NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_sessions UNIQUE (season, event_name, session_type)
);

CREATE TABLE IF NOT EXISTS f1.teams (
    id        SERIAL PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS f1.drivers (
    id           SERIAL PRIMARY KEY,
    abbreviation VARCHAR(10) NOT NULL UNIQUE,
    full_name    VARCHAR(100),
    current_team VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS f1.laps (
    id               BIGSERIAL PRIMARY KEY,
    session_id       INTEGER NOT NULL REFERENCES f1.sessions(id) ON DELETE CASCADE,
    driver_id        INTEGER NOT NULL REFERENCES f1.drivers(id),
    team_id          INTEGER NOT NULL REFERENCES f1.teams(id),
    lap_number       INTEGER NOT NULL,
    lap_time_seconds NUMERIC(9,3),
    CONSTRAINT uq_lap UNIQUE (session_id, driver_id, lap_number)
);

CREATE INDEX IF NOT EXISTS idx_laps_session ON f1.laps(session_id);
CREATE INDEX IF NOT EXISTS idx_laps_team    ON f1.laps(team_id);
