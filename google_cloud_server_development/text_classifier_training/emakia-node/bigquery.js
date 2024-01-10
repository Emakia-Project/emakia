//const {Storage} = require('@google-cloud/storage');
// Instantiate a storage client
//const storage = new Storage();
//const myBucket = storage.bucket('prediction-results-emakia');


var input_file_data = []
const {BigQuery} = require('@google-cloud/bigquery');
const bigquery = new BigQuery();
  // [END bigquery_client_default_credentials]
async function query() {
    // Queries tweets

    const query = `SELECT id, text, possibly_sensitive
      FROM \`training1emakia.training1_dataset_testingprediction.training1_table_testingprediction\``;

    // For all options, see https://cloud.google.com/bigquery/docs/reference/rest/v2/jobs/query
    const options = {
      query: query,
      // Location must match that of the dataset(s) referenced in the query.
      location: 'US',
    };

    // Run the query as a job
    const [job] = await bigquery.createQueryJob(options);
    console.log(`Job ${job.id} started.`);

    // Wait for the query to finish
    const [rows] = await job.getQueryResults();

    // Print the results
    console.log('Rows:');
	for (let i = 0; i < 10; i++) {
  	  predictTextClassification(rows[i]);
 	 }

 }	
  // [END bigquery_query]
 
const endpointId = '1076406490429915136';
const project = 'training1emakia';
const location = 'us-central1';
const aiplatform = require('@google-cloud/aiplatform');
const {instance, prediction} =
 aiplatform.protos.google.cloud.aiplatform.v1.schema.predict;

// Imports the Google Cloud Model Service Client library
const {PredictionServiceClient} = aiplatform.v1;

// Specifies the location of the api endpoint
const clientOptions = {
 apiEndpoint: 'us-central1-aiplatform.googleapis.com',
};

// Instantiates a client
const predictionServiceClient = new PredictionServiceClient(clientOptions);

async function predictTextClassification(row) {
 // Configure the resources
 const endpoint = `projects/${project}/locations/${location}/endpoints/${endpointId}`;

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
 
 console.log('Predict text classification response');
 console.log(`\ttext : ${row.text}\n`);
 console.log(`\tTwitter Prediction : ${row.possibly_sensitive}\n`); 
 console.log(`\tDeployed model id : ${response.deployedModelId}\n\n`);

 console.log('Prediction results:');

 for (const predictionResultValue of response.predictions) {
   const predictionResult =
     prediction.ClassificationPredictionResult.fromValue(
       predictionResultValue
     );

   for (const [i, label] of predictionResult.displayNames.entries()) {
     console.log(`\tDisplay name: ${label}`);
     console.log(`\tConfidences: ${predictionResult.confidences[i]}`);
     console.log(`\tIDs: ${predictionResult.ids[i]}\n`);
   }
 }
}
query();
