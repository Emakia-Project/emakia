const fs = require('fs');
const readline = require('readline');
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

    return {
        'Sentiment score': sentiment.score,
        'Sentiment magnitude': sentiment.magnitude,
    };
}

async function processCSV(inputFilePath, outputFilePath, numRows) {
    try {
        const fileStream = fs.createReadStream(inputFilePath);
        const rl = readline.createInterface({
            input: fileStream,
            crlfDelay: Infinity,
        });

        const header = (await rl[Symbol.asyncIterator]().next()).value.split(',');

        const csvWriter = createCsvWriter({
            path: outputFilePath,
            header: [
                { id: 'text', title: 'Text' },
                { id: 'Sentiment score', title: 'Sentiment score' },
                { id: 'Sentiment magnitude', title: 'Sentiment magnitude' },
            ],
        });

        const recordsWithSentiment = [];
        let rowCount = 0;

        for await (const line of rl) {
            if (rowCount >= numRows) {
                break; // Stop processing after the specified number of rows
            }

            const recordValues = line.split(',');
            const record = {};

            for (let i = 0; i < header.length; i++) {
                record[header[i]] = recordValues[i];
            }

            const text = record['text'];
            const sentimentResults = await analyzeSentiment(text);

            recordsWithSentiment.push({
                ...record,
                ...sentimentResults,
            });

            rowCount++;
        }

        await csvWriter.writeRecords(recordsWithSentiment);
        console.log(`Sentiment scores added to the new CSV file (${outputFilePath}).`);

        // Close file stream explicitly
        fileStream.close();
    } catch (error) {
        console.error('Error processing CSV:', error);
    }
}

async function quickstart() {
    const inputFilePath = 'tweets-labels-processed.csv';
    const outputFilePath = 'sentiment-analysis.csv';
    const numRowsToProcess = 10; // Specify the number of rows to process
    await processCSV(inputFilePath, outputFilePath, numRowsToProcess);
}

quickstart();


