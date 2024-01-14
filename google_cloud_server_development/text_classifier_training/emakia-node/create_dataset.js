const { BigQuery } = require("@google-cloud/bigquery");
const config = require('./config.js');
const bigquery = new BigQuery();
const fs = require('fs');

async function provisionDB() {
    try {
        const dataSetId = await createDataSet(config.bq.defaultDataSetName);
        console.log('Dataset ID:', dataSetId);
    } catch (error) {
        console.error('Error provisioning DB:', error);
        throw error;
    }
}

async function createDataSet(dataSetName) {
    try {
        const options = {
            location: 'US',
        };

        console.log('Creating dataset:', dataSetName);
        const [dataset] = await bigquery.createDataset(dataSetName, options);
        const dataSetId = dataset.id;
        console.log(`Dataset ${dataSetId} created.`);
        return dataSetId;
    } catch (error) {
        console.error('Error creating dataset:', error);
        throw error;
    }
}


// Execute provisionDB function directly when running this script
async function runScript() {
    try {
        console.log('Starting database provisioning...');
        await provisionDB();
        console.log('Database provisioning completed successfully!');
    } catch (error) {
        console.error('Error during provisioning:', error);
    }
}

// Run the script
runScript();

module.exports = { provisionDB };