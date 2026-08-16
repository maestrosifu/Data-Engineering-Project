# Dockerfile
# Personal Data Ecosystem for Learning Analytics
# Build: docker build -t learning-analytics .
# Run: docker run -p 5432:5432 learning-analytics

FROM postgres:15-alpine

# Set environment variables
ENV POSTGRES_DB=learning_analytics
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=tool123

# Copy schema SQL file to initialization directory
# PostgreSQL will automatically run .sql files in this directory on first startup
COPY Code/schema.sql /docker-entrypoint-initdb.d/01_schema.sql

# Copy data files for reference (optional - can be loaded manually)
COPY Data/ /data/

# Copy Python scripts for convenience
COPY Code/load_data.py /scripts/load_data.py
COPY  Code/queries.py /scripts/queries.py

# Install Python and required packages (for running ETL inside container)
RUN apk add --no-cache python3 py3-pip && \
    pip install --no-cache-dir --break-system-packages psycopg2-binary pandas

# Expose PostgreSQL port
EXPOSE 5432

# Run PostgreSQL (default entrypoint)
CMD ["postgres"]
