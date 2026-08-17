# Docker Setup Instructions

**Personal Data Ecosystem for Learning Analytics**

---

## Quick Start (1 Command)

```bash
# Clone the repository
git clone https://github.com/maestrosifu/Data-Engineering-Project.git
cd Data-Engineering-Project

# Copy environment template and configure (optional)
cp .env.template .env

# Start the database with Docker Compose
docker-compose up -d

# Verify the database is ready
docker-compose ps
```

That's it! The PostgreSQL database is now running with the complete schema loaded.

---

## What Happens Automatically

1. **Docker builds** the image from `Dockerfile`
2. **PostgreSQL 15** starts in a container
3. **schema.sql** runs automatically on first startup (creates 6 tables, 0 errors)
4. **Volume persistence** ensures data survives container restarts
5. **Port 5433** is exposed for local connections

---

## Verify the Setup

### Check Container Status
```bash
docker-compose ps
```

Expected output:
```
NAME                              STATUS          PORTS
learning_analytics_postgres       Up 5 seconds    0.0.0.0:5433->5432/tcp
```

### Connect to Database
```bash
# Option 1: From host machine (requires psql installed)
psql -h localhost -p 5433 -U postgres -d learning_analytics

# Option 2: From inside container
docker-compose exec postgres psql -U postgres -d learning_analytics

# Option 3: Verify schema was created
docker-compose exec postgres psql -U postgres -d learning_analytics -c "\dt"
```

Expected output:
```
              List of relations
 Schema |        Name         | Type  | Owner
--------+---------------------+-------+----------
 public | academic_performance | table | postgres
 public | nutrition_logs      | table | postgres
 public | students            | table | postgres
 public | whoop_cycles        | table | postgres
 public | whoop_sleep         | table | postgres
 public | whoop_workouts      | table | postgres
```

---

## Load Data into Database

### Option 1: Run ETL from Host (Recommended)

```bash
# Make sure you're in the Data-Engineering-Project root directory
python Code/load_data.py
```

Expected output:
```
2026-06-12 07:51:56  INFO  Connected to PostgreSQL database 'learning_analytics'
2026-06-12 07:51:56  INFO  Loading whoop_cycles...
2026-06-12 07:51:56  INFO    whoop_cycles: 267 rows in CSV → 267 rows now in DB
...
2026-06-12 07:51:56  INFO  All tables loaded successfully.
```

### Option 2: Run ETL Inside Container

```bash
docker-compose exec postgres python /scripts/load_data.py
```

Note: For this to work, you need to first modify `load_data.py` to use environment variables or update `DB_CONFIG` to point to localhost.

---

## Run Analytical Queries

### From Host Machine
```bash
python Code/queries.py
```

Expected output:
```
============================================================
  Learning Analytics — Query Results
  Database: learning_analytics on localhost
============================================================

============================================================
  Q1 — Average and range of daily active minutes
  ...
```

### From Inside Container
```bash
docker-compose exec postgres python /scripts/queries.py
```

---

## Common Commands

### View Container Logs
```bash
docker-compose logs postgres
```

### Stop the Container
```bash
docker-compose down
```

The database data is preserved (stored in named volume `postgres_data`).

### Stop and Remove Everything (Including Data)
```bash
docker-compose down -v
```

**Warning:** This removes the database volume — data will be lost!

### Restart Container (Keep Data)
```bash
docker-compose restart postgres
```

### Rebuild Image (if Dockerfile Changed)
```bash
docker-compose build --no-cache
docker-compose up -d
```

---

## Troubleshooting

### Port 5433 Already in Use
If you get an error like `Bind for 0.0.0.0:5433 failed: port is already allocated`:

Option 1: Stop existing PostgreSQL
```bash
# On macOS/Linux
sudo systemctl stop postgresql

# Or find and stop the container using port 5433
docker ps | grep 5433
docker stop <container_id>
```

Option 2: Use a different port
```bash
# 5433 is already this project's default (chosen to avoid clashing
# with a local Postgres install on the standard 5432). If 5433 is
# also taken, edit docker-compose.yml and change ports to e.g.:
# ports:
#   - "5434:5432"  # Host:Container

docker-compose up -d
```

### Database Connection Refused
```bash
# Check if container is running
docker-compose ps

# Check container logs
docker-compose logs postgres

# Verify health
docker-compose exec postgres pg_isready -U postgres
```

### Schema Not Created
```bash
# Check if schema.sql was executed
docker-compose exec postgres psql -U postgres -d learning_analytics -c "\dt"

# Manually run schema if needed
docker-compose exec postgres psql -U postgres -d learning_analytics -f /docker-entrypoint-initdb.d/01_schema.sql
```

---

## File Structure for Docker

For Docker to work, your repository should look like:

```
Data-Engineering-Project/
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Container orchestration
├── .env.template              # Environment variables template
├── Code/
│   ├── schema.sql             # Loaded on startup
│   ├── load_data.py
│   ├── queries.py
│   └── load_log.txt
├── Data/
│   ├── Student 1/
│   ├── Student 2/
│   ├── Student 3/
│   └── academic_performance.csv
└── Reports/
    └── *.docx
```

---

## Environment Variables

Edit `.env` to customize:

```bash
# Database name
DB_NAME=learning_analytics

# PostgreSQL user (default: postgres)
DB_USER=postgres

# PostgreSQL password (default: tool123)
DB_PASSWORD=tool123

# Port (default: 5433)
DB_PORT=5433
```

Changes take effect when you run `docker-compose up -d` again.

---

## Persistence & Backups

### Automatic Backups
To backup your database:

```bash
docker-compose exec postgres pg_dump -U postgres learning_analytics > backup_$(date +%Y%m%d_%H%M%S).sql
```

Restore from backup:
```bash
docker-compose exec postgres psql -U postgres -d learning_analytics < backup_20260612_075156.sql
```

### Volume Persistence
Docker automatically saves data to a named volume (`postgres_data`).  
The database persists even if you stop and restart the container:

```bash
docker-compose down    # Data preserved
docker-compose up -d   # Database resumes with existing data
```

---

## Next Steps

1. **Verify setup:** `docker-compose ps` shows container running
2. **Load data:** `python Code/load_data.py`
3. **Run queries:** `python Code/queries.py`
4. **Check logs:** Check `Code/load_log.txt` for success

---

## Production Considerations

For production use, consider:

- ✅ Use `.env` for secrets (not committed to Git)
- ✅ Enable SSL/TLS encryption for connections
- ✅ Set stronger PostgreSQL passwords
- ✅ Configure automatic backups (pg_dump cron job)
- ✅ Set resource limits (`mem_limit`, `cpus` in docker-compose.yml)
- ✅ Use health checks (already included)
- ✅ Configure logging rotation (already included)
- ✅ Monitor with tools like Prometheus or Grafana

---

**For questions or issues, see the main README.md**
