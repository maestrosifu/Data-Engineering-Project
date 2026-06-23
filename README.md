# Data Engineering Project
# Personal Data Ecosystem Learning Analytics
**Introduction Data Engineering**

A pipeline that combines WHOOP wearable data, MyFitnessPal nutrition logs, and academic records from three students over 89 days (Sep–Nov 2024) to explore how lifestyle habits relate to academic performance.

---

## What We're Building

An ETL system that extracts personal health and learning data from CSV files, loads it into a PostgreSQL database, and runs analytical queries to answer five research questions about sleep, activity, nutrition, and grades.

---

## Research Question

> **How do daily lifestyle habits — sleep duration, physical activity, and nutrition — relate to student study time and academic performance?**

## Sub Questions

1. What is the average and range of daily active minutes across all students, and how does it vary between individuals?
2. How does a student's workout and study schedule relate to their sleep duration and physiological load?
3. Is there a relationship between sleep duration and study hours logged the following week?
4. Do students with higher daily active minutes achieve better academic grades?
5. On days with below-average caloric intake, do students log fewer study hours and score lower on nearby assessments?

---

## Data Sources

| Source | Files | Rows |
|---|---|---|
| WHOOP Physiological Cycles | 3 | 267 |
| WHOOP Sleep Records | 3 | 267 |
| WHOOP Workouts | 3 | 140 |
| MyFitnessPal Nutrition | 3 | 624 |
| Academic Performance | 1 | 45 |

---

## Roadmap

✅ **Phase 1 — Dataset Analysis**
- Document all five data sources (structure, columns, data types, granularity)
- Identify and describe missing value patterns per source
- Summarize key statistics per student (recovery, sleep, grades, nutrition)
- Analyze differences in temporal granularity between sources and their ETL implications

✅ **Phase 2 — Database Technology Analysis**
- Compare PostgreSQL, InfluxDB, MongoDB, and Apache Cassandra
- Evaluate each against the specific properties of the dataset
- Select and motivate PostgreSQL as the primary database
- Document rejected alternatives with arguments

✅ **Phase 3 — System Design**
- Relational schema: 6 tables, primary/foreign keys, CHECK constraints, indexes
- ETL pipeline design: extract → transform → load with idempotency and NULL handling
- Distributed architecture: primary + streaming replication standby, ACID consistency, CAP position
- Data security policy: AES-256 encryption, RBAC + Row-Level Security, pg_dump backups, GDPR compliance, ISO 27001:2022 mapping

✅ **Phase 4 — Implementation**
- `schema.sql` — full PostgreSQL schema with constraints and indexes
- `load_data.py` — Python ETL script ingesting all 11 CSV files (< 200 ms runtime)
- `queries.py` — five analytical queries each using at least two data sources:
  - Q1: Average and range of daily active minutes across all students
  - Q2: Workout schedule vs sleep duration and physiological load (day_strain)
  - Q3: Sleep duration vs study hours in the week before each exam
  - Q4: Average daily active minutes vs academic grades (7-day pre-exam window)
  - Q5: Below-average caloric intake weeks vs study hours and assessment scores (2-level CTE)

✅ **Phase 5 — Test Report**
- System test: all 5 tables loaded with correct row counts (1,371 rows total)
- Idempotency confirmed: second pipeline run produces no duplicate rows
- Constraint validation: CHECK violations correctly rejected and rolled back
- CASCADE delete: GDPR right-to-erasure confirmed across all 6 tables atomically
- Query performance: all 5 queries complete in < 10 ms; index use confirmed via EXPLAIN

---

## Tech Stack

- **Database:** PostgreSQL 14
- **Language:** Python 3 (`psycopg2`, `pandas`)
- **Data:** CSV exports from WHOOP, MyFitnessPal, and institutional academic records

---

## Repository Structure

```
Data-Engineering-Project/
├── Code/
│   ├── schema.sql          # Creates all 6 tables — run first
│   ├── load_data.py        # ETL pipeline — run after schema.sql
│   ├── queries.py          # 5 analytical queries — run after load_data.py
│   └── load_log.txt        # Auto-generated ETL log (evidence for Section 5)
├── Data/
│   ├── Student 1/          # WHOOP + MyFitnessPal CSVs for S001
│   ├── Student 2/          # WHOOP + MyFitnessPal CSVs for S002
│   ├── Student 3/          # WHOOP + MyFitnessPal CSVs for S003
│   └── academic_performance.csv
└── Reports/
    ├── Report section 1.docx   # Dataset Analysis
    ├── Report section 2.docx   # Database Technology Comparison
    ├── Report section 3.docx   # System Design (schema + ETL + architecture + security)
    ├── Report section 4.docx   # ETL Implementation documentation
    └── Report section 5.docx   # Test Report
    └── Report section 6.docx   # Conclusion and Final Findings  
```

---

## How to Run

```bash
# 1. Create the database schema
psql -U postgres -d learning_analytics -f Code/schema.sql

# 2. Load all CSV data
python Code/load_data.py

# 3. Run analytical queries
python Code/queries.py
```

Update the `DB_CONFIG` dictionary at the top of `load_data.py` and `queries.py` with your local PostgreSQL credentials before running.
