const aiplatform = require('@google-cloud/aiplatform');
const { BigQuery } = require('@google-cloud/bigquery');
const { PredictionServiceClient } = require('@google-cloud/aiplatform').v1;
const projectId = 'training1emakia';
const datasetId = 'dataset_lucile';
const tableId = 'tweets_prediction_result_lucile4';
const endpointId = '1076406490429915136';
const location = 'US';
const locationEndpoint = 'us-central1';
const { instance, prediction } = aiplatform.protos.google.cloud.aiplatform.v1.schema.predict;
async function insertRowsAsStream(datasetId, tableId, rows) {
  const bigqueryClient = new BigQuery();
  try {
    await bigqueryClient
      .dataset(datasetId)
      .table(tableId)
      .insert(rows);
    console.log(`Inserted ${rows.length} rows into ${tableId} for dataset ${datasetId}`);
  } catch (error) {
    console.log("----BQ JSON Error --- \n ", JSON.stringify(error), "\n");
    throw new Error(error);
  }
}
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
      const batchSize = 10000; // Number of rows to process in each batch
  
      for (let startIndex = 0; startIndex < rows.length; startIndex += batchSize) {
        const endIndex = Math.min(startIndex + batchSize, rows.length);
        const batchRows = rows.slice(startIndex, endIndex);
      
        let predictionRows = [];
      
        for (const row of batchRows) {
          const endpoint = `projects/${projectId}/locations/${locationEndpoint}/endpoints/${endpointId}`;
          const predictionInstance = new instance.TextClassificationPredictionInstance({
            content: row.text,
          });
          const instanceValue = predictionInstance.toValue();
          const instances = [instanceValue];
          const request = {
            endpoint,
            instances,
          };
      
          let retryCount = 0;
          const maxRetries = 3; // Adjust the number of retries as needed
      
          while (retryCount < maxRetries) {
            try {
              const [response] = await predictionServiceClient.predict(request);
              // Process the response as before
              break; // Break the loop if successful
            } catch (error) {
              console.error('Error during prediction:', error);
              retryCount++;
              // Add a delay before the next retry
              await new Promise(resolve => setTimeout(resolve, 1000)); // 1-second delay, adjust as needed
            }
          }
      
          if (retryCount === maxRetries) {
            console.error('Max retries reached. Unable to complete prediction for this row.');
            // Handle this situation as needed
          }
          
          const [response] = await predictionServiceClient.predict(request);
          let prediction_results = [];
          for (const predictionResultValue of response.predictions) {
            const predictionResult = prediction.ClassificationPredictionResult.fromValue(predictionResultValue);
            for (const [i, label] of predictionResult.displayNames.entries()) {
              prediction_results.push({
                display_names: label,
                confidences_value: predictionResult.confidences[i],
                predictionids: predictionResult.ids[i],
              });
            }
          }
          const predictionRow = {
            text: row.text,
            twitter_prediction: row.possibly_sensitive,
            model_id: response.deployedModelId,
            tweet_id: row.id,
            prediction_results: prediction_results,
          };
          predictionRows.push(predictionRow);
        }
  
        console.log(`Inserting batch ${startIndex / batchSize + 1} - ${endIndex / batchSize} (${predictionRows.length} rows) into ${tableId} for dataset ${datasetId}`);
        await insertRowsAsStream(datasetId, tableId, predictionRows);
      }
  
    } catch (error) {
      console.error('Error during query and prediction:', error);
    }
  }
  
  queryAndPredict();