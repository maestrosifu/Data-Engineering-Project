"""
queries.py
Personal Data Ecosystem — Learning Analytics
Introduction Data Engineering Group Project

Runs five analytical queries against the PostgreSQL database and prints results.
Run this AFTER load_data.py has successfully loaded all tables.

Usage:
    python queries.py

Each query answers one research sub-question and uses at least two data sources.
"""

import time
import psycopg2
import psycopg2.extras

# =============================================================================
# CONFIGURATION — must match load_data.py
# =============================================================================

DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "learning_analytics",
    "user":     "postgres",
    "password": "tool123",
}


# =============================================================================
# HELPERS
# =============================================================================

def connect():
    """Open a connection to PostgreSQL and return it."""
    return psycopg2.connect(**DB_CONFIG)


def run_query(conn, title, question, sql, sources):
    """
    Execute a single query, print the results, and return elapsed time.

    conn     — open psycopg2 connection
    title    — short label e.g. 'Q1'
    question — the research sub-question this answers
    sql      — the SQL query string
    sources  — list of table names used, for documentation
    """
    print()
    print("=" * 70)
    print(f"  {title}")
    print(f"  {question}")
    print(f"  Sources: {', '.join(sources)}")
    print("=" * 70)

    start = time.perf_counter()

    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(sql)
        rows = cur.fetchall()
        col_names = [desc[0] for desc in cur.description]

    elapsed_ms = (time.perf_counter() - start) * 1000

    # Print column headers
    col_widths = [max(len(str(name)), max((len(str(r[name])) for r in rows), default=0))
                  for name in col_names]
    header = "  " + "  ".join(str(n).ljust(w) for n, w in zip(col_names, col_widths))
    print(header)
    print("  " + "-" * (sum(col_widths) + 2 * len(col_widths)))

    for row in rows:
        line = "  " + "  ".join(str(row[n]).ljust(w) for n, w in zip(col_names, col_widths))
        print(line)

    print()
    print(f"  {len(rows)} row(s) returned  |  execution time: {elapsed_ms:.2f} ms")

    return elapsed_ms


# =============================================================================
# QUERIES
# =============================================================================

# Q1 ─────────────────────────────────────────────────────────────────────────
# Sub-question: What is the average and range of daily active minutes across
# all students, and how does it vary between individuals?
#
# Design note: "daily active minutes" = duration_min from whoop_workouts.
# Days with no workout contribute 0 active minutes, not NULL.
# We use a subquery to aggregate multiple workouts per day first,
# then average across all 89 days per student.
#
# Sources used: whoop_cycles (to get every day), whoop_workouts (duration)
# ─────────────────────────────────────────────────────────────────────────────

Q1_SQL = """
SELECT
    c.student_id,
    ROUND(AVG(COALESCE(w.daily_min, 0)), 1)  AS avg_daily_active_min,
    MIN(COALESCE(w.daily_min, 0))             AS min_daily_active_min,
    MAX(COALESCE(w.daily_min, 0))             AS max_daily_active_min,
    COUNT(CASE WHEN w.daily_min > 0 THEN 1 END) AS workout_days,
    COUNT(c.cycle_date)                        AS total_days
FROM whoop_cycles c
LEFT JOIN (
    -- Sum duration per day in case a student had more than one session
    SELECT student_id, workout_date, SUM(duration_min) AS daily_min
    FROM whoop_workouts
    GROUP BY student_id, workout_date
) w ON c.student_id = w.student_id AND c.cycle_date = w.workout_date
GROUP BY c.student_id
ORDER BY c.student_id;
"""


# Q2 ─────────────────────────────────────────────────────────────────────────
# Sub-question: How does a student's workout schedule relate to their sleep
# duration and daily physiological load?
#
# Design note: the original sub-question mentions "step count" which is not
# in the WHOOP dataset. We substitute day_strain (cardiovascular load score)
# from whoop_cycles as a comparable measure of daily physical output.
# The query compares workout days vs rest days per student.
#
# Sources used: whoop_cycles, whoop_sleep, whoop_workouts
# ─────────────────────────────────────────────────────────────────────────────

Q2_SQL = """
SELECT
    c.student_id,
    CASE WHEN w.workout_date IS NOT NULL
         THEN 'Workout day'
         ELSE 'Rest day'
    END                                           AS day_type,
    ROUND(AVG(s.sleep_duration_hrs), 2)           AS avg_sleep_hrs,
    ROUND(AVG(s.sleep_efficiency_pct), 1)         AS avg_sleep_efficiency_pct,
    ROUND(AVG(c.day_strain), 2)                   AS avg_day_strain,
    COUNT(*)                                       AS num_days
FROM whoop_cycles c
JOIN whoop_sleep s
    ON c.student_id = s.student_id AND c.cycle_date = s.sleep_date
LEFT JOIN whoop_workouts w
    ON c.student_id = w.student_id AND c.cycle_date = w.workout_date
GROUP BY
    c.student_id,
    CASE WHEN w.workout_date IS NOT NULL THEN 'Workout day' ELSE 'Rest day' END
ORDER BY c.student_id, day_type DESC;
"""


# Q3 ─────────────────────────────────────────────────────────────────────────
# Sub-question: Is there a relationship between sleep duration and study hours?
#
# Design note: there are no daily study hours in the dataset — study_hours
# is recorded once per exam week (study_hours_prior_week in academic_performance).
# We therefore reframe this as: for each exam, what was the average sleep
# duration in the 7 days beforehand, and how does that relate to reported
# study hours that week?
#
# Sources used: whoop_sleep, academic_performance
# ─────────────────────────────────────────────────────────────────────────────

Q3_SQL = """
SELECT
    ap.student_id,
    ap.course,
    ap.assessment_date,
    ap.study_hours_prior_week,
    ROUND(AVG(s.sleep_duration_hrs), 2)    AS avg_sleep_hrs_prior_week,
    ROUND(AVG(s.sleep_efficiency_pct), 1)  AS avg_sleep_efficiency_prior_week,
    COUNT(s.sleep_date)                    AS sleep_days_recorded
FROM academic_performance ap
JOIN whoop_sleep s
    ON  ap.student_id = s.student_id
    AND s.sleep_date >= ap.assessment_date - INTERVAL '7 days'
    AND s.sleep_date <  ap.assessment_date
GROUP BY
    ap.student_id, ap.course, ap.assessment_date, ap.study_hours_prior_week
ORDER BY ap.student_id, ap.assessment_date;
"""


# Q4 ─────────────────────────────────────────────────────────────────────────
# Sub-question: Do students with higher daily active minutes achieve better
# academic grades?
#
# Design note: we calculate average daily active minutes in the 7 days before
# each exam and compare it to the grade received. This links workout intensity
# directly to academic outcomes at the same time window.
#
# Sources used: whoop_cycles, whoop_workouts, academic_performance
# ─────────────────────────────────────────────────────────────────────────────

Q4_SQL = """
SELECT
    ap.student_id,
    ap.course,
    ap.assessment_date,
    ap.grade,
    ROUND(AVG(COALESCE(w.duration_min, 0)), 1) AS avg_daily_active_min_prior_week,
    ROUND(AVG(c.recovery_score_pct), 1)        AS avg_recovery_prior_week
FROM academic_performance ap
JOIN whoop_cycles c
    ON  ap.student_id = c.student_id
    AND c.cycle_date >= ap.assessment_date - INTERVAL '7 days'
    AND c.cycle_date <  ap.assessment_date
LEFT JOIN whoop_workouts w
    ON  c.student_id = w.student_id AND c.cycle_date = w.workout_date
GROUP BY
    ap.student_id, ap.course, ap.assessment_date, ap.grade
ORDER BY ap.student_id, ap.assessment_date;
"""


# Q5 ─────────────────────────────────────────────────────────────────────────
# Sub-question: On days with below-average caloric intake, do students log
# fewer study hours and score lower on nearby assessments?
#
# Design note: we calculate each student's overall average daily calorie intake
# first, then for each exam we measure the average intake in the prior 7 days
# and flag whether it was below that personal average. We then compare
# study hours and grade between the two groups.
#
# Sources used: nutrition_logs, academic_performance
# ─────────────────────────────────────────────────────────────────────────────

Q5_SQL = """
WITH daily_kcal AS (
    -- Total calories per student per day (sum across all meal slots)
    SELECT student_id, log_date, SUM(calories_kcal) AS total_kcal
    FROM nutrition_logs
    GROUP BY student_id, log_date
),
student_avg_kcal AS (
    -- Each student's overall average daily caloric intake across the 89 days
    SELECT student_id, ROUND(AVG(total_kcal), 0) AS overall_avg_kcal
    FROM daily_kcal
    GROUP BY student_id
),
exam_nutrition AS (
    -- For each exam, average daily calories in the 7 days before
    SELECT
        ap.student_id,
        ap.course,
        ap.assessment_date,
        ap.grade,
        ap.study_hours_prior_week,
        ROUND(AVG(dc.total_kcal), 0)  AS avg_kcal_prior_week,
        COUNT(dc.log_date)             AS logged_days_prior_week
    FROM academic_performance ap
    LEFT JOIN daily_kcal dc
        ON  ap.student_id = dc.student_id
        AND dc.log_date >= ap.assessment_date - INTERVAL '7 days'
        AND dc.log_date <  ap.assessment_date
    GROUP BY
        ap.student_id, ap.course, ap.assessment_date,
        ap.grade, ap.study_hours_prior_week
)
SELECT
    en.student_id,
    en.course,
    en.assessment_date,
    en.grade,
    en.study_hours_prior_week,
    en.avg_kcal_prior_week,
    sa.overall_avg_kcal,
    en.logged_days_prior_week,
    CASE
        WHEN en.avg_kcal_prior_week IS NULL THEN 'No data'
        WHEN en.avg_kcal_prior_week < sa.overall_avg_kcal THEN 'Below average'
        ELSE 'At or above average'
    END AS caloric_intake_category
FROM exam_nutrition en
JOIN student_avg_kcal sa ON en.student_id = sa.student_id
ORDER BY en.student_id, en.assessment_date;
"""


# =============================================================================
# MAIN — runs all five queries in order and prints a summary
# =============================================================================

def main():
    print()
    print("=" * 70)
    print("  Learning Analytics — Query Results")
    print(f"  Database: {DB_CONFIG['dbname']} on {DB_CONFIG['host']}")
    print("=" * 70)

    conn = connect()

    timings = {}

    try:
        timings["Q1"] = run_query(
            conn,
            title    = "Q1 — Average and range of daily active minutes",
            question = "What is the average and range of daily active minutes per student?",
            sql      = Q1_SQL,
            sources  = ["whoop_cycles", "whoop_workouts"],
        )

        timings["Q2"] = run_query(
            conn,
            title    = "Q2 — Workout schedule vs sleep quality",
            question = "How does a student's workout schedule relate to sleep duration and strain?",
            sql      = Q2_SQL,
            sources  = ["whoop_cycles", "whoop_sleep", "whoop_workouts"],
        )

        timings["Q3"] = run_query(
            conn,
            title    = "Q3 — Sleep duration vs study hours (week before exam)",
            question = "Is there a relationship between sleep duration and study hours logged?",
            sql      = Q3_SQL,
            sources  = ["whoop_sleep", "academic_performance"],
        )

        timings["Q4"] = run_query(
            conn,
            title    = "Q4 — Daily active minutes vs academic grades",
            question = "Do students with higher active minutes achieve better grades?",
            sql      = Q4_SQL,
            sources  = ["whoop_cycles", "whoop_workouts", "academic_performance"],
        )

        timings["Q5"] = run_query(
            conn,
            title    = "Q5 — Caloric intake vs study hours and assessment scores",
            question = "Do below-average calorie weeks correlate with lower grades and study hours?",
            sql      = Q5_SQL,
            sources  = ["nutrition_logs", "academic_performance"],
        )

    finally:
        conn.close()

    # Print execution time summary (useful for the test report in Phase 5)
    print()
    print("=" * 70)
    print("  Execution time summary")
    print("=" * 70)
    for q, ms in timings.items():
        print(f"  {q}: {ms:.2f} ms")
    print()


if __name__ == "__main__":
    main()
