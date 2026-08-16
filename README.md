[README_UPDATE.md](https://github.com/user-attachments/files/31115743/README_UPDATE.md)
# Data Engineering Project
# Personal Data Ecosystem for Learning Analytics
**Introduction to Data Engineering**

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
| **TOTAL** | **11** | **1,371** |

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
- System test: all 6 tables loaded with correct row counts (1,343 rows in DB, 1 duplicate filtered)
- Idempotency confirmed: second pipeline run produces no duplicate rows
- Constraint validation: CHECK violations correctly rejected and rolled back
- CASCADE delete: GDPR right-to-erasure confirmed across all 6 tables atomically
- Query performance: all 5 queries complete in < 10 ms; index use confirmed via EXPLAIN

---

## Tech Stack

- **Database:** PostgreSQL 15 (via Docker)
- **Language:** Python 3.10+ (`psycopg2`, `pandas`)
- **Container:** Docker & Docker Compose
- **Data:** CSV exports from WHOOP, MyFitnessPal, and institutional academic records

---

## Repository Structure

```
Data-Engineering-Project/
├── Dockerfile                           # Docker image definition
├── docker-compose.yml                   # Container orchestration
├── .env.template                        # Environment variables template
├── DOCKER_SETUP.md                      # Docker setup instructions
├── PROJECT_PLAN.md                      # Project plan & timeline
├── README.md                            # This file
├── Code/
│   ├── schema.sql                       # Creates all 6 tables
│   ├── load_data.py                     # ETL pipeline
│   ├── queries.py                       # 5 analytical queries
│   └── load_log.txt                     # ETL execution log
├── Data/
│   ├── Student 1/                       # WHOOP + MyFitnessPal CSVs for S001
│   ├── Student 2/                       # WHOOP + MyFitnessPal CSVs for S002
│   ├── Student 3/                       # WHOOP + MyFitnessPal CSVs for S003
│   └── academic_performance.csv
└── Reports/
    ├── Report section 1.docx            # Dataset Analysis
    ├── Report section 2.docx            # Database Technology Comparison
    ├── Report section 3 (Final Version).docx   # System Design
    ├── Report section 4 ETL Implementation.docx
    ├── Report section 5 (Test Report).docx
    └── Final_Report_Research_Findings.docx
```

---

## Quick Start (With Docker)

**Prerequisites:** Docker Desktop installed (https://www.docker.com/products/docker-desktop)

### 1. Start PostgreSQL in Docker

```bash
docker-compose up -d
```

This will:
- Build a PostgreSQL 15 container
- Automatically run `schema.sql` (create 6 tables)
- Expose port 5433 on your machine
- Keep data persistent across restarts

### 2. Verify Docker is Running

```bash
docker-compose ps
```

Expected output:
```
NAME                          IMAGE                    STATUS
learning_analytics_postgres   learning-analytics:latest   Up (healthy)
```

### 3. Load Data

```bash
python3 Code/load_data.py
```

Expected output:
```
Connected to PostgreSQL database 'learning_analytics'
Loading whoop_cycles...
  whoop_cycles: 267 rows in CSV → 267 rows now in DB
Loading whoop_sleep...
  whoop_sleep: 267 rows in CSV → 267 rows now in DB
...
All tables loaded successfully.
```

### 4. Run Analytical Queries

```bash
python3 Code/queries.py
```

This runs all 5 queries and prints results:
- Q1: Average and range of daily active minutes
- Q2: Workout schedule vs sleep duration
- Q3: Sleep duration vs study hours (pre-exam)
- Q4: Active minutes vs academic grades
- Q5: Below-average caloric intake vs grades

---

## How to Run (Manual Setup Without Docker)

If you prefer to install PostgreSQL locally:

```bash
# 1. Create the database schema
psql -U postgres -d learning_analytics -f Code/schema.sql

# 2. Load all CSV data
python3 Code/load_data.py

# 3. Run analytical queries
python3 Code/queries.py
```

Update the `DB_CONFIG` dictionary at the top of `load_data.py` and `queries.py` with your local PostgreSQL credentials.

---

## Docker Commands Reference

```bash
# Start containers
docker-compose up -d

# Stop containers (data preserved)
docker-compose down

# View logs
docker-compose logs postgres

# Stop and delete everything (including data)
docker-compose down -v

# Restart containers
docker-compose restart postgres
```

See `DOCKER_SETUP.md` for complete troubleshooting guide.

---

## System Requirements

### With Docker (Recommended)
- Docker Desktop (4.0+)
- 2GB RAM available
- 500MB disk space

### Without Docker
- PostgreSQL 15
- Python 3.10+
- `psycopg2-binary` and `pandas` libraries

---

## Project Timeline

| Phase | Week | Deliverable | Status |
|-------|------|-------------|--------|
| Planning | 1-2 | PROJECT_PLAN.md | ✅ Complete |
| Data Collection | 3-6 | 11 CSVs (1,371 rows) | ✅ Complete |
| Section 1 | 7 | Dataset Analysis | ✅ Complete |
| Section 2 | 8 | Database Technology Analysis | ✅ Complete |
| Section 3 | 9 | System Design | ✅ Complete |
| Section 4 | 10 | ETL Implementation | ✅ Complete |
| Section 5 | 11 | Test Report | ✅ Complete |
| Final Report | 12 | Research Findings | ✅ Complete |
| Infrastructure | 13 | Docker Setup + Documentation | ✅ Complete |

---

## Key Findings

### Per-Student Analysis
- **S001 (Alex)**: Highest discipline — avg 8.36 grade, consistent sleep (7.85h), 56% active days
- **S002 (Jordan)**: Moderate — avg 6.93 grade, variable sleep (6.2h), 53% active days
- **S003 (Casey)**: Lower engagement — avg 5.51 grade, poor sleep (5.42h), 48% active days

### Lifestyle Insights
- Students with consistent sleep perform better academically
- Weekly active minutes show weak correlation with grades (causation unclear)
- Below-average nutrition weeks correlate with lower grades in following exams
- Sleep in the 7 days before exam is strongest predictor of performance

---

## References

- **Comenius Project:** Applied research on personalised education and Learning Analytics
- **WHOOP API:** Physiological and sleep metrics
- **MyFitnessPal API:** Nutrition logging
- **PostgreSQL:** Relational database with GDPR-compliant design

---

## Contributors

- **Rodrigo** (S001): Data collection, dataset analysis
- **Rafael** (S002): Database design, ETL implementation
- **Daniel** (S003): Analysis, testing, Docker setup
- **Group:** Sections 2-3, Final Report, Presentation

---

## Next Steps

To contribute or reproduce:

1. Clone the repository
2. `docker-compose up -d` (start PostgreSQL)
3. `python3 Code/load_data.py` (load data)
4. `python3 Code/queries.py` (run queries)
5. See `Reports/` for detailed findings

For troubleshooting: See `DOCKER_SETUP.md`

