FROM --platform=linux/amd64 gradescope/autograder-base:latest

ARG LOCAL_TEST=false

# Install system dependencies including MySQL
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    mysql-server \
    mysql-client \
    libmysqlclient-dev

# Configure MySQL directories and permissions
RUN mkdir -p /var/run/mysqld /var/lib/mysql \
    && chown -R mysql:mysql /var/run/mysqld /var/lib/mysql \
    && chmod 777 /var/run/mysqld /var/lib/mysql

# Initialize MySQL with a default configuration
RUN mysqld --initialize-insecure --user=mysql --datadir=/var/lib/mysql || true

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy autograder's .env file
COPY .env /autograder/source/.env

COPY source /autograder/source
COPY submission /autograder/sample_submission

RUN if [ "${LOCAL_TEST}" = "true" ]; then \
    cp -r /autograder/sample_submission /autograder/submission/; \
    fi

# Copy your test files and scripts
RUN cd /autograder/source && cp run_autograder /autograder/run_autograder

# Make run_autograder executable
RUN chmod +x /autograder/run_autograder

# Create necessary directories
RUN mkdir -p /autograder/results