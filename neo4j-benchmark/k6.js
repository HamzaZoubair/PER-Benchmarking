import http from 'k6/http';
import { sleep } from 'k6';




export const options = {
  vus: 10,
  iterations: 3000,
  ext: {
    loadimpact: {
      // Project: neo4j
      projectID: 3680687,
      // Test runs with the same name groups test runs together.
      name: 'Write_neo4j'
    }
  },

};

export default function() {
    const url = 'http://0.0.0.0:5000/write_neo4j';
    const read_url = 'http://0.0.0.0:5000/read';

    // generate a random number 
    const number = Math.floor(Math.random() * 1000);


    // Example data to send in the request body
    const payload = {
        "number": {number}
    };

    // Set headers to indicate JSON content
    const headers = {
        'Content-Type': 'application/json',
    };

    // Send a POST request to the /write_neo4j route
    http.post(url, JSON.stringify(payload), { headers: headers });
    //http.post(read_url);
    sleep(1);
}

