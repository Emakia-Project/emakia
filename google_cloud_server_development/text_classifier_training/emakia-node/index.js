const config = require('./config.js');
const { project, location, datasetDisplayName } = config;

// Imports the Google Cloud Dataset Service Client library
const {DatasetServiceClient} = require('@google-cloud/aiplatform');

// Specifies the location of the api endpoint
const clientOptions = {
  apiEndpoint: 'us-central1-aiplatform.googleapis.com',
};

// Instantiates a client
const datasetServiceClient = new DatasetServiceClient(clientOptions);

async function createDatasetText() {
  // Configure the parent resource
  const parent = `projects/${project}/locations/${location}`;
  // Configure the dataset resource
  const dataset = {
    displayName: datasetDisplayName,
    metadataSchemaUri:
      'gs://google-cloud-aiplatform/schema/dataset/metadata/text_1.0.0.yaml',
  };
  const request = {
    parent,
    dataset,
  };

  // Create Dataset Request
  const [response] = await datasetServiceClient.createDataset(request);
  console.log(`Long running operation: ${response.name}`);

  // Wait for operation to complete
  await response.promise();
  const result = response.result;

  console.log('Create dataset text response');
  console.log(`Name : ${result.name}`);
  console.log(`Display name : ${result.displayName}`);
  console.log(`Metadata schema uri : ${result.metadataSchemaUri}`);
  console.log(`Metadata : ${JSON.stringify(result.metadata)}`);
  console.log(`Labels : ${JSON.stringify(result.labels)}`);
}
createDatasetText();