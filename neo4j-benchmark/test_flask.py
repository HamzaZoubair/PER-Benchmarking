from flask import Flask, jsonify, request
import time
from py2neo import Graph
from neo4j import GraphDatabase
import random

app = Flask(__name__)

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def create_job_and_pipeline(self, number):
        try:
            start_time = time.time()
            with self._driver.session() as session:
                tx = session.begin_transaction()

                # Create JenkinsPipeline node
                tx.run("CREATE (p:JenkinsPipeline {name: $job_name})", job_name="Job" + str(number))

                # Create JenkinsJob node and relationship with JenkinsPipeline
                tx.run(
                    """
                    MATCH (p:JenkinsPipeline {name: $job_name})
                    CREATE (j:JenkinsJob {
                        build_number: $build_number,
                        job_name: $job_name,
                        commit_id: $commit_id
                    })
                    CREATE (j)-[:BELONGS_TO]->(p)
                    """,
                    build_number=number,
                    job_name="Job" + str(number),
                    commit_id="Commit" + str(number)
                )

                # Create ContainerImage node and relationship with JenkinsJob
                tx.run(
                    """
                    MATCH (j:JenkinsJob {job_name: $job_name})
                    CREATE (c:ContainerImage {
                        name: $container_name,
                        tag: $tag
                    })
                    CREATE (c)-[:BUILT_BY]->(j)
                    """,
                    job_name="Job" + str(number),
                    container_name="Image" + str(number),
                    tag="Tag" + str(number)
                )

                # Create BaseImage node and relationship with ContainerImage
                tx.run(
                    """
                    MATCH (c:ContainerImage {name: $container_name})
                    CREATE (b:BaseImage {
                        sha: $base_image_sha
                    })
                    CREATE (c)-[:USES_BASE_IMAGE]->(b)
                    """,
                    container_name="Image" + str(number),
                    base_image_sha="BaseImage{'number': " + str(number) + "}"
                )

                # Create SCMRepository node and relationship with JenkinsJob
                tx.run(
                    """
                    MATCH (j:JenkinsJob {job_name: $job_name})
                    CREATE (s:SCMRepository {
                        name: $scm_repo_name
                    })
                    CREATE (j)-[:USES_SCM]->(s)
                    """,
                    job_name="Job" + str(number),
                    scm_repo_name="SCM" + str(number)
                )

                tx.commit()

        except Exception as e:
            print(f"Error: {e}")
        finally:
            print("Neo4j transaction completed.")

    def read(self, number):
        job_name = "Job" + str(number)
        container_name = "Image" + str(number)

        try:
            with self._driver.session() as session:
                result = session.run(
                    """
                    MATCH (c:ContainerImage {name: $container_name})-[:BUILT_BY]->(j:JenkinsJob {job_name: $job_name})
                    OPTIONAL MATCH (c)-[:USES_BASE_IMAGE]->(b:BaseImage)
                    RETURN j, c, b
                    """,
                    job_name=job_name,
                    container_name=container_name
                )

                print(f"Job Name: {job_name}")
                print(f"Container Name: {container_name}")

                for record in result:
                    jenkins_job = record['j']
                    container_image = record['c']
                    base_image = record['b']

                    print("Jenkins Job Data:")
                    print(f"Build Number: {jenkins_job['build_number']}")
                    print(f"Commit ID: {jenkins_job['commit_id']}")
                    
                    print("Container Image Data:")
                    print(f"Container Name: {container_image['name']}")
                    print(f"Tag: {container_image['tag']}")

                    if base_image:
                        print("Base Image Data:")
                        print(f"SHA: {base_image['sha']}")
                    else:
                        print("No Base Image associated with the Container Image.")

        except Exception as e:
            print(f"Error: {e}")



@app.route('/read', methods=['POST'])
def read():
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "password"

    neo4j_connection = Neo4jConnection(uri, username, password)
    neo4j_connection.read(727)
    return jsonify({"message": "Data successfully read from Neo4j"})


@app.route('/write_neo4j', methods=['POST'])
def write_to_neo4j():
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "password"

    neo4j_connection = Neo4jConnection(uri, username, password)
    data = request.json
    neo4j_connection.create_job_and_pipeline(data["number"]["number"])

    # Return a response to the client
    return jsonify({"message": "Data successfully written to Neo4j"})

if __name__ == '__main__':
    app.run(debug=True)



