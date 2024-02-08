import psycopg2

# Function to execute SQL commands
def execute_sql_command(sql_command):
    try:
        conn = psycopg2.connect(
            dbname="mydatabase",
            user="myuser",
            password="mypassword",
            host="localhost",  # Replace with your host if necessary
            port="5432"  # Replace with your PostgreSQL port if necessary
        )
        cursor = conn.cursor()
        cursor.execute(sql_command)
        conn.commit()
        print("Command executed successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

# SQL commands to create tables with corrected syntax
create_tables_sql = """
CREATE TABLE JenkinsPipeline (
    name VARCHAR(255) PRIMARY KEY
);

CREATE TABLE JenkinsJob (
    build_number INT PRIMARY KEY,
    job_name VARCHAR(255) REFERENCES JenkinsPipeline(name) UNIQUE
);
CREATE TABLE BaseImage(
    sha VARCHAR(255) PRIMARY KEY
);

CREATE TABLE ContainerRepository(
    name VARCHAR(255) PRIMARY KEY
);

CREATE TABLE SCMRepository(
    name VARCHAR(255) PRIMARY KEY
);

CREATE TABLE HelmChart(
    name VARCHAR(255) PRIMARY KEY,
    version VARCHAR(255),
    container VARCHAR(255) REFERENCES ContainerRepository(name)
);

CREATE TABLE ContainerImage(
    sha VARCHAR(255) PRIMARY KEY,
    repository VARCHAR(255),
    built_by VARCHAR(255) REFERENCES JenkinsJob(job_name),
    code_from VARCHAR(255) REFERENCES SCMRepository(name),
    base_image VARCHAR(255) REFERENCES BaseImage(sha)
);


"""

# Execute SQL commands
execute_sql_command(create_tables_sql)
