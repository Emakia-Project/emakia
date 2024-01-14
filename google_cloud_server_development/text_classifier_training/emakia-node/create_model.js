const config = require('./config.js');
const { project, location, datasetId, modelDisplayName, trainingPipelineDisplayName } = config;

const aiplatform = require('@google-cloud/aiplatform');
const {definition} =
  aiplatform.protos.google.cloud.aiplatform.v1.schema.trainingjob;

// Imports the Google Cloud Pipeline Service Client library
const {PipelineServiceClient} = aiplatform.v1;

// Specifies the location of the api endpoint
const clientOptions = {
  apiEndpoint: 'us-central1-aiplatform.googleapis.com',
};

// Instantiates a client
const pipelineServiceClient = new PipelineServiceClient(clientOptions);

async function createTrainingPipelineTextClassification() {
  // Configure the parent resource
  const parent = `projects/${project}/locations/${location}`;

  const trainingTaskInputObj = new definition.AutoMlTextClassificationInputs({
    multiLabel: false,
  });
  const trainingTaskInputs = trainingTaskInputObj.toValue();

  const modelToUpload = {displayName: modelDisplayName};
  const inputDataConfig = {datasetId: datasetId};
  const trainingPipeline = {
    displayName: trainingPipelineDisplayName,
    trainingTaskDefinition:
      'gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_text_classification_1.0.0.yaml',
    trainingTaskInputs,
    inputDataConfig,
    modelToUpload,
  };
  const request = {
    parent,
    trainingPipeline,
  };

  // Create training pipeline request
  const [response] = await pipelineServiceClient.createTrainingPipeline(
    request
  );

  console.log('Create training pipeline text classification response :');
  console.log(`Name : ${response.name}`);
  console.log('Raw response:');
  console.log(JSON.stringify(response, null, 2));
}
createTrainingPipelineTextClassification();