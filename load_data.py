"""
load_data.py
Personal Data Ecosystem — Learning Analytics
Introduction Data Engineering Group Project

Reads all 11 CSV files and loads them into the PostgreSQL database.
Run this AFTER schema.sql has been executed.

Usage:
    python load_data.py

Requirements:
    pip install psycopg2-binary pandas
"""

import os
import glob
import logging
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# =============================================================================
# CONFIGURATION — edit these to match your setup
# =============================================================================

DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "learning_analytics",   # name of the database you created
    "user":     "postgres",             # your PostgreSQL username
    "password": "tool123",             # your PostgreSQL password
}

# Folder where your CSV files live (relative to this script)
# Expected structure:
#   data/
#     Student 1/whoop_S001_physiological_cycles.csv
#     Student 1/whoop_S001_sleep.csv
#     Student 1/whoop_S001_workouts.csv
#     Student 1/myfitnesspal_S001_nutrition.csv
#     Student 2/  ... same pattern for S002
#     Student 3/  ... same pattern for S003
#     academic_performance.csv
DATA_DIR = "data"

# =============================================================================
# LOGGING — writes progress to console and to load_log.txt
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.StreamHandler(),                    # print to console
        logging.FileHandler("load_log.txt", "w"),   # save to file
    ],
)
log = logging.getLogger(__name__)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def connect():
    """Open a connection to PostgreSQL and return it."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        log.info("Connected to PostgreSQL database '%s'", DB_CONFIG["dbname"])
        return conn
    except psycopg2.OperationalError as e:
        log.error("Could not connect to the database: %s", e)
        log.error("Check DB_CONFIG at the top of this script.")
        raise


def load_table(conn, sql, rows, table_name, expected_count=None):
    """
    Insert a list of rows into the database inside a single transaction.
    Uses ON CONFLICT DO NOTHING so re-running the script is safe.

    conn          — open psycopg2 connection
    sql           — INSERT statement with %s placeholder for values
    rows          — list of tuples to insert
    table_name    — used only for log messages
    expected_count— if provided, warns if DB row count doesn't match
    """
    if not rows:
        log.warning("  %s: no rows to insert, skipping.", table_name)
        return

    with conn:                          # 'with conn' wraps everything in a transaction
        with conn.cursor() as cur:
            execute_values(cur, sql, rows)
            inserted = cur.rowcount
            # rowcount with execute_values can be -1 on some drivers;
            # do a COUNT to get the real number
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            db_count = cur.fetchone()[0]

    log.info(
        "  %s: %d rows in CSV → %d rows now in DB",
        table_name, len(rows), db_count,
    )

    if expected_count is not None and db_count != expected_count:
        log.warning(
            "  %s: expected %d rows but found %d — check for duplicates or load errors",
            table_name, expected_count, db_count,
        )


def to_date(value):
    """
    Convert a timestamp string like '2024-09-02T00:00:00' to a date string
    '2024-09-02' that PostgreSQL accepts as DATE.
    If value is already a plain date string, return it unchanged.
    """
    if pd.isna(value):
        return None
    s = str(value).strip()
    # Take only the date portion (first 10 characters: YYYY-MM-DD)
    return s[:10]


def to_float_or_none(value):
    """Convert a value to float, returning None if it's empty or not a number."""
    if pd.isna(value):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def to_int_or_none(value):
    """Convert a value to int, returning None if it's empty or not a number."""
    if pd.isna(value):
        return None
    try:
        return int(float(value))   # float() first handles '42.0' strings
    except (ValueError, TypeError):
        return None


def to_bool(value):
    """Convert 'Yes'/'No' strings to Python True/False for PostgreSQL BOOLEAN."""
    if pd.isna(value):
        return None
    return str(value).strip().lower() in ("yes", "true", "1")


def extract_student_id(filepath):
    """
    Pull the student ID (S001, S002, S003) out of a filename.
    e.g. 'myfitnesspal_S002_nutrition.csv' → 'S002'
    """
    filename = os.path.basename(filepath)
    for sid in ["S001", "S002", "S003"]:
        if sid in filename:
            return sid
    raise ValueError(f"Could not extract student_id from filename: {filename}")


# =============================================================================
# LOADERS — one function per table
# =============================================================================

def load_whoop_cycles(conn):
    """Load all three WHOOP physiological cycle CSV files."""
    log.info("Loading whoop_cycles...")

    files = glob.glob(os.path.join(DATA_DIR, "**", "*physiological_cycles*.csv"), recursive=True)
    if not files:
        log.error("  No physiological cycle files found in %s", DATA_DIR)
        return

    all_rows = []
    for filepath in sorted(files):
        df = pd.read_csv(filepath, dtype=str)   # read everything as string first
        log.info("  Read %d rows from %s", len(df), os.path.basename(filepath))

        for _, row in df.iterrows():
            all_rows.append((
                str(row["student_id"]).strip(),
                to_date(row["cycle_start_time"]),            # cycle_date
                row["cycle_start_time"],
                row["cycle_end_time"],
                to_float_or_none(row["recovery_score_pct"]),
                to_float_or_none(row["hrv_rmssd_milli"]),
                to_int_or_none(row["resting_heart_rate_bpm"]),
                to_float_or_none(row["day_strain"]),
                to_int_or_none(row["energy_burned_cal"]),
                to_int_or_none(row["avg_heart_rate_bpm"]),
                to_int_or_none(row["max_heart_rate_bpm"]),
                to_float_or_none(row["respiratory_rate_rpm"]),
                to_float_or_none(row["blood_oxygen_pct"]),
                to_float_or_none(row["skin_temp_celsius"]),
            ))

    sql = """
        INSERT INTO whoop_cycles (
            student_id, cycle_date, cycle_start_time, cycle_end_time,
            recovery_score_pct, hrv_rmssd_milli, resting_heart_rate_bpm,
            day_strain, energy_burned_cal, avg_heart_rate_bpm,
            max_heart_rate_bpm, respiratory_rate_rpm, blood_oxygen_pct,
            skin_temp_celsius
        ) VALUES %s
        ON CONFLICT (student_id, cycle_date) DO NOTHING
    """
    load_table(conn, sql, all_rows, "whoop_cycles", expected_count=267)


def load_whoop_sleep(conn):
    """Load all three WHOOP sleep CSV files."""
    log.info("Loading whoop_sleep...")

    files = glob.glob(os.path.join(DATA_DIR, "**", "*sleep*.csv"), recursive=True)
    # Exclude any file that also matches 'cycles' or 'workout' just in case
    files = [f for f in files if "cycles" not in f and "workout" not in f]
    if not files:
        log.error("  No sleep files found in %s", DATA_DIR)
        return

    all_rows = []
    for filepath in sorted(files):
        df = pd.read_csv(filepath, dtype=str)
        log.info("  Read %d rows from %s", len(df), os.path.basename(filepath))

        for _, row in df.iterrows():
            all_rows.append((
                str(row["student_id"]).strip(),
                to_date(row["sleep_start_time"]),            # sleep_date
                row["sleep_start_time"],
                row["sleep_end_time"],
                to_float_or_none(row["sleep_duration_hrs"]),
                to_float_or_none(row["sleep_needed_hrs"]),
                to_float_or_none(row["sleep_performance_pct"]),
                to_float_or_none(row["sleep_efficiency_pct"]),
                to_float_or_none(row["rem_sleep_hrs"]),
                to_float_or_none(row["sws_deep_sleep_hrs"]),
                to_float_or_none(row["light_sleep_hrs"]),
                to_float_or_none(row["awake_hrs"]),
                to_float_or_none(row["sleep_consistency_pct"]),
                to_float_or_none(row["respiratory_rate_rpm"]),
            ))

    sql = """
        INSERT INTO whoop_sleep (
            student_id, sleep_date, sleep_start_time, sleep_end_time,
            sleep_duration_hrs, sleep_needed_hrs, sleep_performance_pct,
            sleep_efficiency_pct, rem_sleep_hrs, sws_deep_sleep_hrs,
            light_sleep_hrs, awake_hrs, sleep_consistency_pct,
            respiratory_rate_rpm
        ) VALUES %s
        ON CONFLICT (student_id, sleep_date) DO NOTHING
    """
    load_table(conn, sql, all_rows, "whoop_sleep", expected_count=267)


def load_whoop_workouts(conn):
    """Load all three WHOOP workout CSV files."""
    log.info("Loading whoop_workouts...")

    files = glob.glob(os.path.join(DATA_DIR, "**", "*workout*.csv"), recursive=True)
    if not files:
        log.error("  No workout files found in %s", DATA_DIR)
        return

    all_rows = []
    for filepath in sorted(files):
        df = pd.read_csv(filepath, dtype=str)
        log.info("  Read %d rows from %s", len(df), os.path.basename(filepath))

        for _, row in df.iterrows():
            # distance_km is empty for gym sports — convert to None (NULL in DB)
            distance = to_float_or_none(row.get("distance_km", None))

            all_rows.append((
                str(row["student_id"]).strip(),
                to_date(row["workout_start_time"]),          # workout_date
                row["workout_start_time"],
                str(row.get("sport", "")).strip() or None,
                to_float_or_none(row["workout_strain"]),
                to_int_or_none(row["duration_min"]),
                to_int_or_none(row["avg_heart_rate_bpm"]),
                to_int_or_none(row["max_heart_rate_bpm"]),
                to_int_or_none(row["calories_burned"]),
                distance,
            ))

    sql = """
        INSERT INTO whoop_workouts (
            student_id, workout_date, workout_start_time, sport,
            workout_strain, duration_min, avg_heart_rate_bpm,
            max_heart_rate_bpm, calories_burned, distance_km
        ) VALUES %s
        ON CONFLICT DO NOTHING
    """
    load_table(conn, sql, all_rows, "whoop_workouts", expected_count=140)


def load_nutrition(conn):
    """
    Load all three MyFitnessPal nutrition CSV files.
    NOTE: these files do NOT have a student_id column — it is injected
    from the filename (e.g. myfitnesspal_S002_nutrition.csv → 'S002').
    """
    log.info("Loading nutrition_logs...")

    files = glob.glob(os.path.join(DATA_DIR, "**", "*nutrition*.csv"), recursive=True)
    if not files:
        log.error("  No nutrition files found in %s", DATA_DIR)
        return

    all_rows = []
    for filepath in sorted(files):
        student_id = extract_student_id(filepath)   # inject from filename
        df = pd.read_csv(filepath, dtype=str)
        log.info("  Read %d rows from %s (student: %s)", len(df), os.path.basename(filepath), student_id)

        for _, row in df.iterrows():
            # food_notes is always empty in this dataset but we keep the column
            notes = str(row.get("food_notes", "")).strip() or None

            all_rows.append((
                student_id,
                str(row["date"]).strip(),
                str(row["meal"]).strip(),
                to_int_or_none(row["calories_kcal"]),
                to_float_or_none(row["protein_g"]),
                to_float_or_none(row["carbohydrates_g"]),
                to_float_or_none(row["fat_g"]),
                to_float_or_none(row.get("fiber_g", None)),
                to_float_or_none(row.get("sugar_g", None)),
                to_int_or_none(row.get("sodium_mg", None)),
                to_int_or_none(row.get("water_ml", None)),
                notes,
            ))

    sql = """
        INSERT INTO nutrition_logs (
            student_id, log_date, meal, calories_kcal, protein_g,
            carbohydrates_g, fat_g, fiber_g, sugar_g, sodium_mg,
            water_ml, food_notes
        ) VALUES %s
        ON CONFLICT (student_id, log_date, meal) DO NOTHING
    """
    load_table(conn, sql, all_rows, "nutrition_logs", expected_count=624)


def load_academic(conn):
    """
    Load the academic performance CSV.
    This is the only combined file (all students in one file with student_id column).
    'Yes'/'No' in submission_on_time is converted to True/False.
    """
    log.info("Loading academic_performance...")

    files = glob.glob(os.path.join(DATA_DIR, "**", "*academic*.csv"), recursive=True)
    # Also check the root data folder directly
    root_file = os.path.join(DATA_DIR, "academic_performance.csv")
    if os.path.exists(root_file) and root_file not in files:
        files.append(root_file)

    if not files:
        log.error("  No academic performance file found in %s", DATA_DIR)
        return

    all_rows = []
    for filepath in sorted(files):
        df = pd.read_csv(filepath, dtype=str)
        log.info("  Read %d rows from %s", len(df), os.path.basename(filepath))

        for _, row in df.iterrows():
            all_rows.append((
                str(row["student_id"]).strip(),
                str(row["course"]).strip(),
                str(row["assessment_type"]).strip(),
                str(row["assessment_date"]).strip(),
                to_float_or_none(row["grade"]),
                to_float_or_none(row["study_hours_prior_week"]),
                to_bool(row["submission_on_time"]),   # 'Yes' → True, 'No' → False
            ))

    sql = """
        INSERT INTO academic_performance (
            student_id, course, assessment_type, assessment_date,
            grade, study_hours_prior_week, submission_on_time
        ) VALUES %s
        ON CONFLICT (student_id, course, assessment_type, assessment_date) DO NOTHING
    """
    load_table(conn, sql, all_rows, "academic_performance", expected_count=45)


# =============================================================================
# MAIN — runs all loaders in order
# =============================================================================

def main():
    log.info("=" * 60)
    log.info("ETL pipeline starting at %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log.info("=" * 60)

    conn = connect()

    try:
        load_whoop_cycles(conn)
        load_whoop_sleep(conn)
        load_whoop_workouts(conn)
        load_nutrition(conn)
        load_academic(conn)

        log.info("=" * 60)
        log.info("All tables loaded successfully.")
        log.info("=" * 60)

    except Exception as e:
        log.error("Pipeline failed: %s", e)
        raise

    finally:
        conn.close()
        log.info("Database connection closed.")


if __name__ == "__main__":
    main()
