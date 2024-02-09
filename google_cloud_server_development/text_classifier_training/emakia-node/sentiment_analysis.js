const fs = require('fs');
const csv = require('csv-parser');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const language = require('@google-cloud/language');

async function analyzeSentiment(text) {
    const client = new language.LanguageServiceClient();

    const document = {
        content: text,
        type: 'PLAIN_TEXT',
    };

    const [result] = await client.analyzeSentiment({ document: document });
    const sentiment = result.documentSentiment;

    console.log(`Text: ${text}`);
    console.log(`Sentiment score: ${sentiment.score}`);
    console.log(`Sentiment magnitude: ${sentiment.magnitude}`);

    return {
        'Sentiment score': sentiment.score,
        'Sentiment magnitude': sentiment.magnitude,
    };
}

async function processCSV(inputFilePath, outputFilePath) {
    try {
        const records = [];
        const fileStream = fs.createReadStream(inputFilePath);

        const parser = csv()
            .on('data', (data) => records.push(data))
            .on('end', async () => {
                if (records.length === 0) {
                    console.error('No records found in the CSV file.');
                    return;
                }

                const text = records[0]['text'];
                const sentimentResults = await analyzeSentiment(text);

                const recordsWithSentiment = records.map((record) => ({
                    'text': record['text'],
                    ...sentimentResults,
                }));

                const csvWriter = createCsvWriter({
                    path: outputFilePath,
                    header: [
                        { id: 'text', title: 'Text' },
                        { id: 'Sentiment score', title: 'Sentiment score' },
                        { id: 'Sentiment magnitude', title: 'Sentiment magnitude' },
                    ],
                });

                await csvWriter.writeRecords(recordsWithSentiment);
                console.log(`Sentiment scores added to the new CSV file (${outputFilePath}).`);
            })
            .on('error', (error) => {
                console.error('Error reading CSV:', error);
            });

        fileStream.pipe(parser);
    } catch (error) {
        console.error('Error processing CSV:', error);
    }
}

async function quickstart() {
    const inputFilePath = 'tweets-labels-processed.csv';
    const outputFilePath = 'sentiment-analysis.csv';
    await processCSV(inputFilePath, outputFilePath);
}

quickstart();
