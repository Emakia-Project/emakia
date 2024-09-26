const { BigQuery } = require('@google-cloud/bigquery');
const fs = require('fs');
const path = require('path');

async function exportTableToJson() {
    // Specify the BigQuery table to export
    const projectId = 'emakia';
    const datasetId = 'politics';
    const tableId = 'tweets';

    // Specify the directory and file path where you want to save the JSON file
    const directoryPath = './tweets-/politics/';
    const fileName = 'politics-tweets.json';
    const filePath = path.join(directoryPath, fileName);

    try {
        // Create the directory if it doesn't exist
        if (!fs.existsSync(directoryPath)) {
            fs.mkdirSync(directoryPath, { recursive: true });
            console.log(`Directory '${directoryPath}' created.`);
        }

        // Create a BigQuery client
        const bigquery = new BigQuery();

        // Get table metadata
        const [table] = await bigquery.dataset(datasetId).table(tableId).get();

        // Get table schema
        const schema = table.metadata.schema;

        // Define pagination options
        const pageSize = 1000; // Adjust this value based on your requirements
        let pageToken = null;

        // Initialize an empty array to store all data
        let allData = [];

        // Paginate through the results and accumulate data
        do {
            // Run query to select a page of data from the table
            const options = {
                query: `SELECT * FROM \`${projectId}.${datasetId}.${tableId}\` LIMIT ${pageSize}`,
                location: 'US', // Update with your dataset's location
                pageToken: pageToken,
            };
            const [rows, metadata] = await bigquery.query(options);

            // Accumulate data
            allData = allData.concat(rows);

            // Update page token for the next page (if any)
            pageToken = metadata && metadata.pageToken ? metadata.pageToken : null;
        } while (pageToken);

        // Prepare data
        const data = allData.map(row => {
            const nestedData = {};
            schema.fields.forEach(field => {
                const fieldName = field.name;
                if (row[fieldName] !== undefined) {
                    // Check if the field is nested
                    if (field.type === 'RECORD') {
                        nestedData[fieldName] = row[fieldName];
                    } else {
                        nestedData[fieldName] = row[fieldName];
                    }
                }
            });
            return nestedData;
        });

        // Write data to JSON file
        fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
        console.log(`Data exported to ${filePath}`);
    } catch (err) {
        console.error('Error exporting data:', err);
    }
}

// Call the function to export data to JSON
exportTableToJson();


