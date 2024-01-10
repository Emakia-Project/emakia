const aiplatform = require('@google-cloud/aiplatform');
const { BigQuery } = require("@google-cloud/bigquery");
const { PredictionServiceClient } = require('@google-cloud/aiplatform').v1;

const projectId = 'training1emakia';
const datasetId = 'bq_dataset_Mie';
const tableId = 'tweet_prediction_results_Mie';
const endpointId = '5701603307739414528';
const location = 'US';
const locationEndpoint = 'us-central1';
const {instance, prediction} =
 aiplatform.protos.google.cloud.aiplatform.v1.schema.predict;

async function insertRowsAsStream(datasetId, tableId, rows) {
    const bigqueryClient = new BigQuery();
    // Insert data into a table
    try {
      const result = await new Promise((resolve, reject) => {
        bigqueryClient
          .dataset(datasetId)
          .table(tableId)
          .insert(rows)
          .then((results) => {
            console.log(`Inserted ${rows.length} rows into ${tableId} for dataset ${datasetId}`);
            resolve(rows);
          })
          .catch((err) => {
            reject(err);
          });
      });
    } catch (error) {
      console.log("----BQ JSON Error --- \n ", JSON.stringify(error), "\n");
      throw new Error(error);
    }
  }

// Function to perform query and prediction
async function queryAndPredict() {
  const bigquery = new BigQuery();
  const query = `SELECT id, text, possibly_sensitive
    FROM \`training1emakia.training1_dataset_testingprediction.training1_table_testingprediction\``;

  const options = {
    query: query,
    location: location,
  };

  try {
    const [job] = await bigquery.createQueryJob(options);
    console.log(`Job ${job.id} started.`);

    const [rows] = await job.getQueryResults();

    const clientOptions = {
      apiEndpoint: 'us-central1-aiplatform.googleapis.com',
    };
    const predictionServiceClient = new PredictionServiceClient(clientOptions);

    let predictionRows = [];
    for (let i = 0; i < rows.length; i++) {
      const row = rows[i];
      const endpoint = `projects/${projectId}/locations/${locationEndpoint}/endpoints/${endpointId}`;

      const predictionInstance =
        new instance.TextClassificationPredictionInstance({
            content: row.text,
        });
      const instanceValue = predictionInstance.toValue();

      const instances = [instanceValue];
      const request = {
        endpoint,
        instances,
      };
      const [response] = await predictionServiceClient.predict(request);
      
    const displayName = "";
    let prediction_results = [];
      for (const predictionResultValue of response.predictions) {
        const predictionResult =
          prediction.ClassificationPredictionResult.fromValue(
            predictionResultValue
          );
        for (const [i, label] of predictionResult.displayNames.entries()) {
          const displayName = label;
          prediction_results.push({
            display_names: label,
            confidences_value: predictionResult.confidences[i],
            predictionids: predictionResult.ids[i],
          })
        //   console.log(`\tDisplay name: ${label}`);
        //   console.log(`\tConfidences: ${predictionResult.confidences[i]}`);
        //   console.log(`\tIDs: ${predictionResult.ids[i]}\n`);
        }
      }
      
    //   console.log(`response : ${response}`)
    //   console.log(`model id : ${response.deployedModelId}`);
    //   console.log(`tweet id : ${row.id}`);
    //   console.log(`tweet pred : ${row.possibly_sensitive}`);
      const predictionRow = {
        text: row.text,
        twitter_prediction: row.possibly_sensitive,
        model_id: response.deployedModelId,
        tweet_id: row.id,
        prediction_results: prediction_results
      };
    
      predictionRows.push(predictionRow);
    }
    
    // predictionRows.push(predictionRow);
    console.log(`${predictionRows}`)
    // Insert predicted data into BigQuery
    await insertRowsAsStream(datasetId, tableId, predictionRows);
    
  } catch (error) {
    console.error('Error during query and prediction:', error);
  }
}

// Run the query and prediction process
queryAndPredict();