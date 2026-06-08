# Data Engineering Project
# Personal Data Ecosystem Learning Analytics
**Introduction Data Engineering**

A pipeline that combines WHOOP wearable data, MyFitnessPal nutrition logs, and academic records from three students over 89 days (Sep–Nov 2024) to explore how lifestyle habits relate to academic performance.

---

## What We're Building

An ETL system that extracts personal health and learning data from CSV files, loads it into a PostgreSQL database, and runs analytical queries to answer five research questions about sleep, activity, nutrition, and grades.

---

## Research Question

> **How do daily lifestyle habits sleep duration, physical activity, and nutrition relate to student study time and academic performance?**

## Sub Questions

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

## Roadmap
✅ Phase 1 — Dataset Analysis

 Document all five data sources (structure, columns, data types, granularity)
 Identify and describe missing value patterns per source
 Summarize key statistics per student (recovery, sleep, grades, nutrition)
 Analyze differences in temporal granularity between sources and their implications for aggregation

✅ Phase 2 — Database Technology Analysis

 Compare PostgreSQL, InfluxDB, MongoDB, and Apache Cassandra
 Evaluate each against the specific properties of the dataset (join support, time series handling, schema flexibility, missing data)
 Select and motivate PostgreSQL as the primary database
 Document rejected alternatives with arguments

🔲 Phase 3 — System Design

 Define the relational schema (tables, primary keys, foreign keys, constraints)
 Design the ETL pipeline (Extract from CSV → Transform → Load into PostgreSQL)
 Describe the distributed architecture:

 Central PostgreSQL server setup
 Replication strategy (streaming replication for read replica)
 Fault tolerance and failover approach
 Consistency guarantees (ACID) and why sharding is not needed at this scale


 Write the Data Security Policy:

 Encryption at rest and in transit (SSL/TLS)
 Role-based access control (per student roles + analyst role)
 Backup strategy (frequency, retention, storage)
 Logging and monitoring
 GDPR compliance (consent, data minimization, right to erasure, retention policy)
 Reference to ISO 27001 as security framework



🔲 Phase 4 — Implementation

 Write schema.sql, full PostgreSQL schema with constraints and indexes
 Write load_data.py, Python ETL script to ingest all 11 CSV files
 Write queries.py, five analytical queries, each using at least two data sources:

 Q1: Average and range of daily active minutes across all students
 Q2: Workout and study schedule vs. sleep duration and step count
 Q3: Sleep duration vs. study hours logged the following day
 Q4: Average daily active minutes vs. academic grades
 Q5: Below average caloric intake days vs. study hours and assessment scores


 Validate all queries return expected results

🔲 Phase 5 — Test Report

 System test: verify ETL pipeline loads all data correctly (row counts, constraints, nulls)
 Measure query execution time for all five queries
 Document explain plans and any performance observations
 Write up test report with results and conclusions

---

## Tech Stack

- **Database:** PostgreSQL
- **Language:** Python (`psycopg2`)
- **Data:** CSV exports from WHOOP, MyFitnessPal, and institutional records

---
