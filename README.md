# Data-Engineering-Project
# Personal Data Ecosystem — Learning Analytics
**Introduction Data Engineering | Group Project 2024–2025**

A pipeline that combines WHOOP wearable data, MyFitnessPal nutrition logs, and academic records from three students over 89 days (Sep–Nov 2024) to explore how lifestyle habits relate to academic performance.

---

## What We're Building

An ETL system that extracts personal health and learning data from CSV files, loads it into a PostgreSQL database, and runs analytical queries to answer five research questions about sleep, activity, nutrition, and grades.

---

## Research Question

> **How do daily lifestyle habits — sleep duration, physical activity, and nutrition — relate to student study time and academic performance?**

## Sub-Questions

1. What is the average and range of daily active minutes across all students, and how does it vary between individuals?
2. How does a student's workout and study schedule relate to their sleep duration and step count?
3. Is there a relationship between sleep duration and study hours logged the following day?
4. Do students with higher daily active minutes achieve better academic grades?
5. On days with below-average caloric intake, do students log fewer study hours and score lower on nearby assessments?

---

## Project Status

| Section | Topic | Status |
|---|---|---|
| 1 | Dataset Analysis | ✅ Done |
| 2 | Database Technology Comparison & Selection | ✅ Done |
| 3 | System Design & Security Policy | 🔲 To do |
| 4 | Implementation (ETL script + 5 queries) | 🔲 To do |
| 5 | Test Report & Query Performance | 🔲 To do |

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

## Tech Stack

- **Database:** PostgreSQL
- **Language:** Python (`psycopg2`)
- **Data:** CSV exports from WHOOP, MyFitnessPal, and institutional records

---

## Repository Structure

```
/
├── data/               # Raw CSV files (all 11 sources)
├── docs/               # Report sections
├── schema/             # schema.sql
├── scripts/
│   ├── load_data.py    # ETL loading script
│   └── queries.py      # Analytical queries
└── README.md
```
