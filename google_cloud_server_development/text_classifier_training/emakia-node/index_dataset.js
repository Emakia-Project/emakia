const config = require('./config.js');
const { project, location, datasetId } = config;

const gcsSourceUri = "gs://data_lucile/tweets-labels.csv";
// eg. "gs://<your-gcs-bucket>/<import_source_path>/[file.csv/file.jsonl]"


// Imports the Google Cloud Dataset Service Client library
const {DatasetServiceClient} = require('@google-cloud/aiplatform');

// Specifies the location of the api endpoint
const clientOptions = {
  apiEndpoint: 'us-central1-aiplatform.googleapis.com',
};
const datasetServiceClient = new DatasetServiceClient(clientOptions);

async function importDataTextClassificationSingleLabel() {
  const name = datasetServiceClient.datasetPath(project, location, datasetId);
  // Here we use only one import config with one source
  const importConfigs = [
    {
      gcsSource: {uris: [gcsSourceUri]},
      importSchemaUri:
        'gs://google-cloud-aiplatform/schema/dataset/ioformat/text_classification_single_label_io_format_1.0.0.yaml',
    },
  ];
  const request = {
    name,
    importConfigs,
  };

  try { // Import data request
        const [response] = await datasetServiceClient.importData(request);
        console.log(`Long running operation : ${response.name}`);

        // Wait for operation to complete
        const [importDataResponse] = await response.promise();


        console.log(
            `Import data text classification single label response : \
            ${JSON.stringify(importDataResponse.result)} ${JSON.stringify(importDataResponse.response)}`
        );
    } catch (err) {
        console.error(err);
      }
}
importDataTextClassificationSingleLabel();