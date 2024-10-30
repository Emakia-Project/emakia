const { BigQuery } = require('@google-cloud/bigquery');
const fs = require('fs');
const path = require('path');

async function exportTablesFromDatasetToJSON(projectId, datasetId, outputDirectory) {
    try {
        // Create a BigQuery client
        const bigquery = new BigQuery();
        console.log(projectId)
        // Get list of tables in the dataset
        const [tables] = await bigquery.dataset(datasetId).getTables();

        // Loop through each table and export its data to JSON
        for (const table of tables) {
            const tableId = table.id;

            // Specify the file path where you want to save the JSON file for this table
            const fileName = `${tableId}.json`;
            const filePath = path.join(outputDirectory, fileName);

            // Run query to select all data from the table
            const query = `SELECT * FROM \`${projectId}.${datasetId}.${tableId}\``;
            const [rows] = await bigquery.query(query);

            // Prepare data
            const data = rows.map(row => row);

            // Write data to JSON file
            fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
            console.log(`Data exported from table '${tableId}' to ${filePath}`);
        }
    } catch (err) {
        console.error('Error exporting data:', err);
    }
}

// Specify your BigQuery project ID, dataset ID, and output directory
const projectId = 'training1emakia';
console.log(projectId)
const datasetId = 'query_results_training1';
const outputDirectory = './output/Results-training/';

// Call the function to export data from all tables in the dataset to JSON
exportTablesFromDatasetToJSON(projectId, datasetId, outputDirectory);
