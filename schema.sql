-- =============================================================================
-- schema.sql
-- Personal Data Ecosystem — Learning Analytics
-- Introduction Data Engineering Group Project
--
-- Run this file once to create all tables in your PostgreSQL database.
-- Command:  psql -U postgres -d your_database_name -f schema.sql
-- =============================================================================


-- Drop tables in reverse dependency order so we can re-run this file cleanly
-- (CASCADE removes anything that depends on the table being dropped)
DROP TABLE IF EXISTS academic_performance CASCADE;
DROP TABLE IF EXISTS nutrition_logs       CASCADE;
DROP TABLE IF EXISTS whoop_workouts       CASCADE;
DROP TABLE IF EXISTS whoop_sleep          CASCADE;
DROP TABLE IF EXISTS whoop_cycles         CASCADE;
DROP TABLE IF EXISTS students             CASCADE;


-- -----------------------------------------------------------------------------
-- TABLE: students
-- One row per student. All other tables point back to this one via student_id.
-- Deleting a student here cascades to all their rows everywhere else (GDPR).
-- -----------------------------------------------------------------------------
CREATE TABLE students (
    student_id  VARCHAR(4)   PRIMARY KEY,          -- e.g. 'S001'
    name        VARCHAR(100) NOT NULL               -- pseudonymised display name
);

-- Seed the three students
INSERT INTO students (student_id, name) VALUES
    ('S001', 'Rodrigo'),
    ('S002', 'Rafael'),
    ('S003', 'Daniel');


-- -----------------------------------------------------------------------------
-- TABLE: whoop_cycles
-- One row per student per day. Core physiological metrics from the WHOOP device.
-- Unique constraint prevents duplicate days if the ETL script is re-run.
-- -----------------------------------------------------------------------------
CREATE TABLE whoop_cycles (
    cycle_id                SERIAL       PRIMARY KEY,
    student_id              VARCHAR(4)   NOT NULL
                                REFERENCES students(student_id) ON DELETE CASCADE,
    cycle_date              DATE         NOT NULL,
    cycle_start_time        TIMESTAMP    NOT NULL,
    cycle_end_time          TIMESTAMP    NOT NULL,
    recovery_score_pct      NUMERIC(4,1) CHECK (recovery_score_pct BETWEEN 1 AND 99),
    hrv_rmssd_milli         NUMERIC(6,2),
    resting_heart_rate_bpm  INTEGER      CHECK (resting_heart_rate_bpm > 0),
    day_strain              NUMERIC(4,2) CHECK (day_strain BETWEEN 0 AND 21),
    energy_burned_cal       INTEGER,
    avg_heart_rate_bpm      INTEGER,
    max_heart_rate_bpm      INTEGER,
    respiratory_rate_rpm    NUMERIC(4,1),
    blood_oxygen_pct        NUMERIC(4,1) CHECK (blood_oxygen_pct BETWEEN 80 AND 100),
    skin_temp_celsius       NUMERIC(4,2),

    UNIQUE (student_id, cycle_date)
);

CREATE INDEX idx_cycles_student_date ON whoop_cycles(student_id, cycle_date);


-- -----------------------------------------------------------------------------
-- TABLE: whoop_sleep
-- One row per student per night. Detailed sleep architecture from the WHOOP device.
-- Joins to whoop_cycles on (student_id, sleep_date = cycle_date).
-- -----------------------------------------------------------------------------
CREATE TABLE whoop_sleep (
    sleep_id                SERIAL       PRIMARY KEY,
    student_id              VARCHAR(4)   NOT NULL
                                REFERENCES students(student_id) ON DELETE CASCADE,
    sleep_date              DATE         NOT NULL,   -- derived from sleep_start_time
    sleep_start_time        TIMESTAMP    NOT NULL,
    sleep_end_time          TIMESTAMP    NOT NULL,
    sleep_duration_hrs      NUMERIC(4,2) CHECK (sleep_duration_hrs >= 0),
    sleep_needed_hrs        NUMERIC(4,2),
    sleep_performance_pct   NUMERIC(5,1) CHECK (sleep_performance_pct BETWEEN 0 AND 200),
    sleep_efficiency_pct    NUMERIC(4,1) CHECK (sleep_efficiency_pct BETWEEN 0 AND 100),
    rem_sleep_hrs           NUMERIC(4,2),
    sws_deep_sleep_hrs      NUMERIC(4,2),
    light_sleep_hrs         NUMERIC(4,2),
    awake_hrs               NUMERIC(4,2),
    sleep_consistency_pct   NUMERIC(4,1),
    respiratory_rate_rpm    NUMERIC(4,1),

    UNIQUE (student_id, sleep_date)
);

CREATE INDEX idx_sleep_student_date ON whoop_sleep(student_id, sleep_date);


-- -----------------------------------------------------------------------------
-- TABLE: whoop_workouts
-- Sparse event log — rows only exist on days when a workout was recorded.
-- JOIN to whoop_cycles must use LEFT JOIN so rest days are kept in results.
-- distance_km is NULL for gym sports (weightlifting, yoga) — this is intentional.
-- -----------------------------------------------------------------------------
CREATE TABLE whoop_workouts (
    workout_id              SERIAL       PRIMARY KEY,
    student_id              VARCHAR(4)   NOT NULL
                                REFERENCES students(student_id) ON DELETE CASCADE,
    workout_date            DATE         NOT NULL,   -- derived from workout_start_time
    workout_start_time      TIMESTAMP    NOT NULL,
    sport                   VARCHAR(50),
    workout_strain          NUMERIC(4,2) CHECK (workout_strain BETWEEN 0 AND 21),
    duration_min            INTEGER      CHECK (duration_min > 0),
    avg_heart_rate_bpm      INTEGER,
    max_heart_rate_bpm      INTEGER,
    calories_burned         INTEGER,
    distance_km             NUMERIC(6,3)             -- NULL for non-cardio sports
);

CREATE INDEX idx_workouts_student_date ON whoop_workouts(student_id, workout_date);


-- -----------------------------------------------------------------------------
-- TABLE: nutrition_logs
-- Up to 4 rows per student per day (one per meal slot).
-- A missing day means the student did not log — this absence is informative.
-- CHECK on meal ensures only the four valid MyFitnessPal slot names are accepted.
-- -----------------------------------------------------------------------------
CREATE TABLE nutrition_logs (
    log_id          SERIAL       PRIMARY KEY,
    student_id      VARCHAR(4)   NOT NULL
                        REFERENCES students(student_id) ON DELETE CASCADE,
    log_date        DATE         NOT NULL,
    meal            VARCHAR(20)  NOT NULL
                        CHECK (meal IN ('Breakfast', 'Lunch', 'Dinner', 'Snacks')),
    calories_kcal   INTEGER      CHECK (calories_kcal >= 0),
    protein_g       NUMERIC(6,1),
    carbohydrates_g NUMERIC(6,1),
    fat_g           NUMERIC(6,1),
    fiber_g         NUMERIC(6,1),
    sugar_g         NUMERIC(6,1),
    sodium_mg       INTEGER,
    water_ml        INTEGER,
    food_notes      TEXT,        -- empty in this dataset but kept for schema completeness

    UNIQUE (student_id, log_date, meal)
);

CREATE INDEX idx_nutrition_student_date ON nutrition_logs(student_id, log_date);


-- -----------------------------------------------------------------------------
-- TABLE: academic_performance
-- One row per student per assessment (45 total: 3 students × 5 courses × 3 exams).
-- This is the aggregation target — all other sources are rolled up to this level
-- before cross-source comparisons can be made.
-- -----------------------------------------------------------------------------
CREATE TABLE academic_performance (
    record_id               SERIAL       PRIMARY KEY,
    student_id              VARCHAR(4)   NOT NULL
                                REFERENCES students(student_id) ON DELETE CASCADE,
    course                  VARCHAR(100) NOT NULL,
    assessment_type         VARCHAR(20)  NOT NULL
                                CHECK (assessment_type IN ('Exam', 'Final')),
    assessment_date         DATE         NOT NULL,
    grade                   NUMERIC(3,1) CHECK (grade BETWEEN 0 AND 10),
    study_hours_prior_week  NUMERIC(4,1) CHECK (study_hours_prior_week >= 0),
    submission_on_time      BOOLEAN      NOT NULL,

    UNIQUE (student_id, course, assessment_type, assessment_date)
);

CREATE INDEX idx_academic_student_date ON academic_performance(student_id, assessment_date);


-- =============================================================================
-- End of schema.sql
-- After running this file, run load_data.py to populate the tables.
-- =============================================================================
