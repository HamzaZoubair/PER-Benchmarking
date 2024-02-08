from flask import Flask, jsonify, request
import time
import psycopg2


app = Flask(__name__)

class PostgresQLConnection:
    def __init__(self, uri, user, password):
        self._driver = psycopg2.connect(uri, user=user, password=password)

    def close(self):
        self._driver.close()



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
        


    def insert_postgresql(number):
        print(number)
        try:
            conn = psycopg2.connect(
                dbname="mydatabase",
                user="myuser",
                password="mypassword",
                host="localhost",
                port="5432"
            )
            cursor = conn.cursor()

            start_time = time.time()

            ## Insertion into JenkinsPipeline
            pipeline_name = "Job" + str(number)
            cursor.execute("INSERT INTO JenkinsPipeline (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (pipeline_name,))

            # Insertion into JenkinsJob
            cursor.execute("INSERT INTO JenkinsJob (build_number, job_name) VALUES (%s, %s) ON CONFLICT (build_number) DO NOTHING", (number, pipeline_name))

            # Insertion into ContainerRepository
            repository_name = "Repository" + str(number)
            cursor.execute("INSERT INTO ContainerRepository (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (repository_name,))

            # Insertion into SCMRepository
            scm_name = "SCM" + str(number)
            cursor.execute("INSERT INTO SCMRepository (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (scm_name,))

            # Insertion into BaseImage
            base_image_sha = "BaseImage" + str(number)
            cursor.execute("INSERT INTO BaseImage (sha) VALUES (%s) ON CONFLICT (sha) DO NOTHING", (base_image_sha,))

            # Insertion into HelmChart
            chart_name = "Chart" + str(number)
            cursor.execute("INSERT INTO HelmChart (name, version, container) VALUES (%s, %s, %s) ON CONFLICT (name) DO NOTHING", (chart_name, "1.0", repository_name))

            # Insertion into ContainerImage
            image_sha = "Image" + str(number)
            cursor.execute("INSERT INTO ContainerImage (sha, repository, built_by, code_from, base_image) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (sha) DO NOTHING", (image_sha, repository_name, pipeline_name, scm_name, base_image_sha))

            conn.commit()
            print(f"Inserted {number} records into PostgreSQL.")

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Time taken for PostgreSQL: {elapsed_time} seconds")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()

    def read_jenkins_job_data(build_number):
        job = "Job" + str(build_number)
        try:
            conn = psycopg2.connect(
                dbname="mydatabase",
                user="myuser",
                password="mypassword",
                host="localhost",
                port="5432"
            )
            cursor = conn.cursor()

            # Query to retrieve information about a Jenkins job
            query = """
                SELECT ContainerImage.sha AS image_sha, BaseImage.sha AS base_image_sha
                FROM ContainerImage
                JOIN JenkinsJob ON ContainerImage.built_by = JenkinsJob.job_name
                JOIN BaseImage ON ContainerImage.base_image = BaseImage.sha
                WHERE JenkinsJob.job_name = %s;

            """

            cursor.execute(query, (job,))
            result = cursor.fetchone()

            if result:
                job_data = {
                    'build_number': build_number,
                    'job_name': job,
                    'image_sha': result[0] if result[0] else "N/A",
                    'base_image_sha': result[1] if result[1] else "N/A"
                }

                print("Jenkins Job Data:")
                for key, value in job_data.items():
                    print(f"{key}: {value}")

            else:
                print(f"No data found for Jenkins job with build_number {build_number}")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()

@app.route('/init_db', methods=['GET'])
def init_db():
    create_tables_sql = """
CREATE TABLE JenkinsPipeline (
    name VARCHAR(255) PRIMARY KEY
);

CREATE TABLE JenkinsJob (
    build_number VARCHAR(255)  PRIMARY KEY,
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
    PostgresQLConnection.execute_sql_command(create_tables_sql)
    return jsonify({"message": "Initiated successfully"})



@app.route('/insert-postgres', methods=['POST'])
def insert():
    data = request.get_json()
    num_entry = data['number']
    PostgresQLConnection.insert_postgresql(str(num_entry["uniqueNumber"]))
    return jsonify({"message": "Inserted successfully"})


@app.route('/delete-all', methods=['GET'])
def delete_all():
    delete_tables_sql = """
        DROP TABLE JenkinsJob;
        DROP TABLE JenkinsPipeline;
        """
    PostgresQLConnection.execute_sql_command(delete_tables_sql)
    return jsonify({"message": "Deleted successfully"})

@app.route('/read', methods=['POST'])
def read():

    PostgresQLConnection.read_jenkins_job_data("1706963875888625")
    return jsonify({"message": "Inserted successfully"})





if __name__ == '__main__':
    app.run(debug=True)
