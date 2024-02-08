from flask import Flask, jsonify, request
import time
from pymongo import MongoClient

app = Flask(__name__)

class MongoConnection:
    def __init__(self, uri, user, password):
        self._client = MongoClient(uri, username=user, password=password)

    def close(self):
        self._driver.close()

    # Function to insert data into MongoDB
def insert_mongodb(number):
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['mydatabase']
        collection_jenkins_pipeline = db['jenkins_pipeline']
        collection_jenkins_job = db['jenkins_job']
        collection_base_image = db['base_image']
        collection_container_repo = db['container_repository']
        collection_scm_repo = db['scm_repository']
        collection_helm_chart = db['helm_chart']
        collection_container_image = db['container_image']

        start_time = time.time()

        # Insert into JenkinsPipeline
        jenkins_pipeline = {
            "name": "Job" + str(number)
        }
        collection_jenkins_pipeline.insert_one(jenkins_pipeline)

        # Insert into JenkinsJob
        jenkins_job = {
            "build_number": str(number),
            "job_name": jenkins_pipeline["name"],
            "commit_id": "Commit" + str(number)
        }
        collection_jenkins_job.insert_one(jenkins_job)

        # Insert into SCMRepository
        scm_repo = {
            "name": "SCM" + str(number)
        }
        collection_scm_repo.insert_one(scm_repo)

        # Insert into BaseImage
        base_image = {
            "sha": "BaseImage" + str(number)
        }
        collection_base_image.insert_one(base_image)

        # Insert into ContainerRepository
        container_repo = {
            "name": "Repository" + str(number)
        }
        collection_container_repo.insert_one(container_repo)

        # Insert into HelmChart
        helm_chart = {
            "name": "Chart" + str(number),
            "version": "1.0",
            "container": container_repo["name"]
        }
        collection_helm_chart.insert_one(helm_chart)

        # Insert into ContainerImage
        container_image = {
            "built_by": jenkins_pipeline["name"],
            "name": "Image" + str(number),
            "tag": "Tag" + str(number),
            "repository": container_repo["name"],
            "code_from": scm_repo["name"],
            "base_image": base_image["sha"]
        }
        collection_container_image.insert_one(container_image)

        print(f"Inserted {number} record into MongoDB.")

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Time taken for MongoDB: {elapsed_time} seconds")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

def read_mongodb_jenkins_job_data(build_number):
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['mydatabase']
        collection_jenkins_job = db['jenkins_job']
        collection_container_image = db['container_image']
        collection_base_image = db['base_image']

        job_name = "Job{'number': " + str(build_number) + "}"

        # Query to retrieve information about a Jenkins job and its associated base image
        result = collection_jenkins_job.find_one({"job_name": job_name})

        if result:
            container_image = collection_container_image.find_one({"built_by": job_name})

            if container_image:
                base_image_sha = container_image.get("base_image")
                sha = "BaseImage{'number': " + str(base_image_sha) + "}"
                base_image = collection_base_image.find_one({"sha": sha})

                if container_image:
                    
                    base_image_sha = container_image.get("base_image")
                    print(base_image_sha)
                    base_image = collection_base_image.find_one({"sha": base_image_sha})

                    if base_image:
                        job_data = {
                            'build_number': result["build_number"],
                            'job_name': result["job_name"],
                            'base_image_sha': base_image["sha"] if base_image["sha"] else "N/A"
                        }

                        print("Jenkins Job Data:")
                        for key, value in job_data.items():
                            print(f"{key}: {value}")
                    else:
                        print(f"No data found for BaseImage associated with ContainerImage built by Jenkins job {job_name}")
                else:
                    print(f"No data found for ContainerImage built by Jenkins job {job_name}")


    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()



@app.route('/insert', methods=['POST'])
def insert():
    data = request.get_json()
    num_entry = data['number']
    insert_mongodb(num_entry)
    return jsonify({"message": "Inserted successfully"})

@app.route('/read', methods=['POST'])
def read():
    read_mongodb_jenkins_job_data(582)
    return jsonify({"message": "Readed successfully"})



if __name__ == '__main__':
    app.run(debug=True)
