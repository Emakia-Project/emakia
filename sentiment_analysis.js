const fs = require('fs');
const readline = require('readline');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const language = require('@google-cloud/language');

async function analyzeSentimentWithRetry(text, maxRetries = 3) {
    let retries = 0;
    while (retries < maxRetries) {
        try {
            const client = new language.LanguageServiceClient({
                timeout: 900000, // Increase timeout to 15 minutes (900000 milliseconds)
            });

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
        } catch (error) {
            console.error('Error analyzing sentiment:', error);
            retries++;
        }
    }

    return {
        'Sentiment score': 'N/A',
        'Sentiment magnitude': 'N/A',
    };
}
async function processCSV(inputFilePath, outputFilePath, chunkSize) {
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
                { id: 'label', title: 'Label'},
                { id: 'text', title: 'Text' },
                { id: 'Sentiment score', title: 'Sentiment score' },
                { id: 'Sentiment magnitude', title: 'Sentiment magnitude' },
            ],
        });

        let recordsWithSentiment = [];
        let rowCount = 0;

        for await (const line of rl) {
            const recordValues = line.split(',');
            const record = {};

            for (let i = 0; i < header.length; i++) {
                record[header[i]] = recordValues[i];
            }

            const text = record['text'];
            const sentimentResults = await analyzeSentimentWithRetry(text);

            recordsWithSentiment.push({
                ...record,
                ...sentimentResults,
            });

            rowCount++;

            if (rowCount >= chunkSize) {
                await csvWriter.writeRecords(recordsWithSentiment);
                console.log(`Sentiment scores added to the new CSV file for ${rowCount} rows.`);
                recordsWithSentiment = [];
                rowCount = 0;
            }
        }

        // Write remaining records
        if (recordsWithSentiment.length > 0) {
            await csvWriter.writeRecords(recordsWithSentiment);
            console.log(`Sentiment scores added to the new CSV file for the remaining rows.`);
        }

        console.log(`Sentiment scores added to the new CSV file (${outputFilePath}).`);

        // Close file stream explicitly
        fileStream.close();
    } catch (error) {
        console.error('Error processing CSV:', error);
    }
}

async function quickstart() {
    const chunkSize = 1000;
    
    for (let i = 3; i >= 1; i--) {
        const inputFilePath = `tweets-labels-processed-${i}.csv`;
        const outputFilePath = `sentiment-analysis-tweets-labels-processed-${i}.csv`;
        await processCSV(inputFilePath, outputFilePath, chunkSize);
    }
}

quickstart();

