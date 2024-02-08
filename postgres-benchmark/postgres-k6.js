import http from 'k6/http';
import { sleep } from 'k6';




export const options = {
    vus: 10,
    iterations: 3000,
    ext: {
      loadimpact: {
        // Project: mongo
        projectID: 3680640,
        // Test runs with the same name groups test runs together.
        name: 'write_postgres'
      }
    }
  };

export default function() {
    const url = 'http://0.0.0.0:5000/insert-postgres';
    const read_url = 'http://0.0.0.0:5000/read';

    const randomPart = Math.floor(Math.random() * 1000);
    
    // Get the current timestamp in milliseconds
    const timestamp = new Date().getTime();
    
    // Concatenate the timestamp and random number to make it unique
    const uniqueNumber = parseInt(`${timestamp}${randomPart % 1000}`, 10);
    
    // Concatenate the timestamp to the random number

    // Example data to send in the request body
    const payload = {
        "number": {uniqueNumber}
    };

    // Set headers to indicate JSON content
    const headers = {
        'Content-Type': 'application/json',
    };

    // Send a POST request to the /write_neo4j route
    //http.post(url, JSON.stringify(payload), { headers: headers });
    http.post(read_url);
    sleep(1);
}

