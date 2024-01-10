'use strict';

function main(
  datasetId = 'Dataset_Sikieng', // Existing dataset
  tableId = 'tweet_prediction_results_sikieng2', // Table to be created
  schema = [
{name: 'text', type: 'STRING', mode: 'REQUIRED'},  // missing mode every item
{name: 'twitter_prediction', type: 'BOOL', mode: 'REQUIRED'},
{name: 'model_id', type: 'INTEGER', mode: 'REQUIRED'},
{name: 'tweet_id', type: 'INTEGER', mode: 'REQUIRED'},
{name: 'prediction_results',
    type: "RECORD",
    mode: "REPEATED",
    fields: [
    {name: 'display_names', type: 'INTEGER', mode: 'REQUIRED'},
    {name: 'confidences_value', type: 'FLOAT', mode: 'REQUIRED'},
    {name:'predictionids', type: 'INTEGER', mode: 'REQUIRED'},
    ]
  },
]
) {
  // [START bigquery_create_table]
  // Import the Google Cloud client library and create a client
  const {BigQuery} = require('@google-cloud/bigquery');
  const bigquery = new BigQuery();
  async function createTable() {
    // Creates a new table named "my_table" in "my_dataset".
    /**
     * TODO(developer): Uncomment the following lines before running the sample.
     */
    // const datasetId = "my_dataset";
    // const tableId = "my_table";
    // const schema = 'Name:string, Age:integer, Weight:float, IsMagic:boolean';
    // For all options, see https://cloud.google.com/bigquery/docs/reference/v2/tables#resource
    const options = {
      schema: schema,
      location: 'US',
    };
    // Create a new table in the dataset
    const [table] = await bigquery
      .dataset(datasetId)
      .createTable(tableId, options);
    console.log(`Table ${table.id} created.`);
  }
  // [END bigquery_create_table]
  createTable();
}
main(...process.argv.slice(2));